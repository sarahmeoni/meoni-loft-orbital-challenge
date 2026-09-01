#
# test_tracking.py
#
# FlyDevTracker window parsing, overhead detection and caching, using
# requests-mock so no real network calls are made.
#

from datetime import datetime, timezone

import requests

from models.location import Location
from models.satellite import Satellite
from models.tracking_config import TrackingConfig
from tracking.fly import FlyDevTracker

BASE = "https://satellites.fly.dev"


def _config(**overrides):
    params = {
        "backend": "satellites_fly",
        "api_base_url": BASE,
        "poll_interval_seconds": 10,
        "request_timeout_seconds": 10,
        "passes_lookahead_days": 1,
        "refresh_interval_seconds": 3600,
        "min_culmination_degrees": 0.0,
    }
    params.update(overrides)
    return TrackingConfig(**params)


def _pass(rise, fall, alt=45.0):
    return {
        "rise": {"utc_timestamp": rise},
        "set": {"utc_timestamp": fall},
        "culmination": {"alt": alt},
    }


def _at(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _tracker(config, satellites):
    return FlyDevTracker(
        Location(latitude=1.0, longitude=2.0),
        tuple(satellites),
        config,
        session=requests.Session(),
    )


def test_overhead_when_now_inside_window(requests_mock):
    requests_mock.get(f"{BASE}/passes/25544", json=[_pass(100, 200)])
    tracker = _tracker(_config(), [Satellite(25544, "blue")])
    assert tracker.satellites_overhead(_at(150)) == {25544}


def test_not_overhead_outside_window(requests_mock):
    requests_mock.get(f"{BASE}/passes/25544", json=[_pass(100, 200)])
    tracker = _tracker(_config(), [Satellite(25544, "blue")])
    assert tracker.satellites_overhead(_at(300)) == set()


def test_low_culmination_pass_filtered_out(requests_mock):
    requests_mock.get(f"{BASE}/passes/25544", json=[_pass(100, 200, alt=5.0)])
    tracker = _tracker(_config(min_culmination_degrees=10.0), [Satellite(25544, "blue")])
    assert tracker.satellites_overhead(_at(150)) == set()


def test_multiple_satellites_reported_together(requests_mock):
    requests_mock.get(f"{BASE}/passes/25544", json=[_pass(100, 200)])
    requests_mock.get(f"{BASE}/passes/48915", json=[_pass(100, 200)])
    tracker = _tracker(_config(), [Satellite(25544, "blue"), Satellite(48915, "pink")])
    assert tracker.satellites_overhead(_at(150)) == {25544, 48915}


def test_server_error_is_graceful(requests_mock):
    # A 500 must be swallowed (logged) and never crash the poll.
    requests_mock.get(f"{BASE}/passes/25544", status_code=500)
    tracker = _tracker(_config(), [Satellite(25544, "blue")])
    assert tracker.satellites_overhead(_at(150)) == set()


def test_non_list_payload_is_graceful(requests_mock):
    requests_mock.get(f"{BASE}/passes/25544", json={"unexpected": "shape"})
    tracker = _tracker(_config(), [Satellite(25544, "blue")])
    assert tracker.satellites_overhead(_at(150)) == set()


def test_windows_cached_within_refresh_interval(requests_mock):
    matcher = requests_mock.get(f"{BASE}/passes/25544", json=[_pass(100, 100000)])
    tracker = _tracker(_config(refresh_interval_seconds=3600), [Satellite(25544, "blue")])
    tracker.satellites_overhead(_at(150))
    tracker.satellites_overhead(_at(160))
    # Second poll within the interval reuses the cache -> only one HTTP call.
    assert matcher.call_count == 1


def test_cache_refreshes_when_exhausted(requests_mock):
    matcher = requests_mock.get(f"{BASE}/passes/25544", json=[_pass(100, 200)])
    tracker = _tracker(_config(refresh_interval_seconds=3600), [Satellite(25544, "blue")])
    tracker.satellites_overhead(_at(150))
    # All windows are now in the past -> exhaustion forces a refetch.
    tracker.satellites_overhead(_at(500))
    assert matcher.call_count == 2
