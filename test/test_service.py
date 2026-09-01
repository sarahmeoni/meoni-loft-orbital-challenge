#
# test_service.py
#
# LightingService loop: command formatting, quiet-when-empty behaviour,
# tracker-error resilience and clean shutdown. The clock and sleep are
# injected so the loop runs deterministically.
#

from datetime import datetime, timezone

from models.app_config import AppConfig
from models.location import Location
from models.satellite import Satellite
from models.tracking_config import TrackingConfig
from output.base import Output
from service import LightingService
from tracking.base import SatelliteTracker
from utils.errors import TrackingError

SATS = [Satellite(norad_id=25544, color="blue"), Satellite(norad_id=48915, color="pink")]


def _config(satellites=SATS):
    return AppConfig(
        location=Location(latitude=1.0, longitude=2.0),
        tracking=TrackingConfig(),
        satellites=tuple(satellites),
    )


class FakeTracker(SatelliteTracker):
    def __init__(self, results):
        self._results = list(results)
        self.calls = 0

    def satellites_overhead(self, now):
        result = self._results[self.calls]
        self.calls += 1
        if isinstance(result, Exception):
            raise result
        return result


class RecordingOutput(Output):
    def __init__(self):
        self.sent: list[str] = []
        self.closed = False

    def send(self, command):
        self.sent.append(command)

    def close(self):
        self.closed = True


def _at(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def test_tick_formats_command_in_config_order():
    out = RecordingOutput()
    # tracker returns ids out of config order; output must follow config order.
    svc = LightingService(_config(), FakeTracker([{48915, 25544}]), out)
    svc.tick(_at(0))
    assert out.sent == ["25544: blue, 48915: pink"]


def test_tick_emits_single_satellite():
    out = RecordingOutput()
    svc = LightingService(_config(), FakeTracker([{48915}]), out)
    svc.tick(_at(0))
    assert out.sent == ["48915: pink"]


def test_tick_is_quiet_when_none_overhead():
    out = RecordingOutput()
    svc = LightingService(_config(), FakeTracker([set()]), out)
    svc.tick(_at(0))
    assert out.sent == []


def test_tick_handles_tracker_error():
    out = RecordingOutput()
    svc = LightingService(_config(), FakeTracker([TrackingError("down")]), out)
    svc.tick(_at(0))  # must not raise
    assert out.sent == []


def test_run_loops_until_interrupt_and_closes_output():
    out = RecordingOutput()
    tracker = FakeTracker([{25544}, {48915}, set()])

    ticks = {"n": 0}

    def fake_sleep(_seconds):
        ticks["n"] += 1
        if ticks["n"] >= 3:
            raise KeyboardInterrupt

    clock = {"t": 0}

    def fake_now():
        current = clock["t"]
        clock["t"] += 1
        return _at(current)

    svc = LightingService(_config(), tracker, out, sleep=fake_sleep, now=fake_now)
    svc.run()

    assert out.sent == ["25544: blue", "48915: pink"]
    assert out.closed is True
