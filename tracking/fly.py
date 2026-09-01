#
# fly.py
#

import logging
from datetime import datetime

import requests

from models.location import Location
from models.satellite import Satellite
from models.tracking_config import TrackingConfig
from tracking.base import SatelliteTracker
from utils.errors import TrackingError

logger = logging.getLogger(__name__)

# A pass window as (rise_timestamp, set_timestamp) in UTC epoch seconds.
Window = tuple[int, int]


class FlyDevTracker(SatelliteTracker):
    """Tracker uses satellites.fly.dev to predict passes.

    Pass windows are fetched once per satellite and cached; each call then
    only compares ``now`` against the cached windows. The cache is refreshed
    when it expires (default is 1 hour) or when every window has moved into the past.
    """

    def __init__(
        self,
        location: Location,
        satellites: tuple[Satellite, ...],
        config: TrackingConfig,
        session: requests.Session | None = None,
    ) -> None:
        self._location = location
        self._satellites = satellites
        self._config = config
        self._session = session or requests.Session()
        self._windows: dict[int, list[Window]] = {}
        self._last_refresh: datetime | None = None

    def satellites_overhead(self, now: datetime) -> set[int]:
        self._refresh_if_needed(now)
        now_ts = int(now.timestamp())
        overhead: set[int] = set()
        for sat in self._satellites:
            if any(rise <= now_ts <= fall for rise, fall in self._windows.get(sat.norad_id, ())):
                overhead.add(sat.norad_id)
        return overhead

    def _refresh_if_needed(self, now: datetime) -> None:
        stale = self._last_refresh is None or (
            (now - self._last_refresh).total_seconds() >= self._config.refresh_interval_seconds
        )
        if not stale and self._has_active_or_future_windows(int(now.timestamp())):
            return
        for sat in self._satellites:
            self._refresh_satellite(sat)
        self._last_refresh = now

    def _has_active_or_future_windows(self, now_ts: int) -> bool:
        return any(
            fall >= now_ts for windows in self._windows.values() for _, fall in windows
        )

    def _refresh_satellite(self, sat: Satellite) -> None:
        try:
            self._windows[sat.norad_id] = self._to_windows(self._fetch_passes(sat.norad_id))
        except (requests.RequestException, TrackingError, ValueError, KeyError, TypeError) as exc:
            # Keep any previously cached windows so a flaky poll never drops the lights.
            logger.warning("Could not refresh passes for %s: %s", sat.norad_id, exc)

    def _fetch_passes(self, norad_id: int) -> list[dict]:
        url = f"{self._config.api_base_url.rstrip('/')}/passes/{norad_id}"
        params = {
            "lat": self._location.latitude,
            "lon": self._location.longitude,
            "days": self._config.passes_lookahead_days,
        }
        response = self._session.get(
            url, params=params, timeout=self._config.request_timeout_seconds
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise TrackingError(f"Unexpected passes payload for {norad_id}: expected a list.")
        return data

    def _to_windows(self, passes: list[dict]) -> list[Window]:
        windows: list[Window] = []
        for entry in passes:
            culmination_alt = float(entry["culmination"]["alt"])
            if culmination_alt < self._config.min_culmination_degrees:
                continue
            rise_ts = int(entry["rise"]["utc_timestamp"])
            set_ts = int(entry["set"]["utc_timestamp"])
            windows.append((rise_ts, set_ts))
        return windows
