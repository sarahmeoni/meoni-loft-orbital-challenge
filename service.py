#
# service.py
#

import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone

from models.app_config import AppConfig
from output.base import Output
from tracking.base import SatelliteTracker
from utils.const import Constants
from utils.errors import SatelliteLightingError

logger = logging.getLogger(__name__)


class LightingService:
    """Poll the tracker on a fixed interval and emit lighting commands.

    Each tick asks the tracker which satellites are overhead, maps those
    NORAD ids to their colors (in config order) and sends a single command
    line to the outputs. Nothing is emitted while no satellite is overhead.
    """

    def __init__(
        self,
        config: AppConfig,
        tracker: SatelliteTracker,
        output: Output,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._satellites = config.satellites
        self._poll_interval = config.tracking.poll_interval_seconds
        self._tracker = tracker
        self._output = output
        self._sleep = sleep
        self._now = now or (lambda: datetime.now(timezone.utc))

    def run(self) -> None:
        logger.info(
            "Starting satellite-lighting: %d satellites, polling every %ds",
            len(self._satellites),
            self._poll_interval,
        )
        try:
            while True:
                self.tick(self._now())
                self._sleep(self._poll_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down.")
        finally:
            self._output.close()

    def tick(self, now: datetime) -> None:
        try:
            overhead = self._tracker.satellites_overhead(now)
        except SatelliteLightingError as exc:
            logger.warning("Tracker poll failed: %s", exc)
            return
        if not overhead:
            logger.debug("No satellites overhead.")
            return
        self._output.send(self._format_command(overhead))

    def _format_command(self, overhead: set[int]) -> str:
        pairs = [
            f"{sat.norad_id}{Constants.command_kv_separator}{sat.color}"
            for sat in self._satellites
            if sat.norad_id in overhead
        ]
        return Constants.command_pair_separator.join(pairs)
