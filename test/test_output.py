#
# test_output.py
#
# Output sinks, fan-out isolation and the output factory.
#

import pytest

from models.app_config import AppConfig
from models.location import Location
from models.output_config import OutputConfig
from models.tracking_config import TrackingConfig
from output.base import Output
from output.factory import build_output
from output.file import FileOutput
from output.multi import MultiOutput
from output.tcp import TcpOutput
from utils.errors import ConfigError


class RecordingOutput(Output):
    def __init__(self):
        self.sent: list[str] = []
        self.closed = False

    def send(self, command):
        self.sent.append(command)

    def close(self):
        self.closed = True


class FailingOutput(Output):
    def send(self, command):
        raise RuntimeError("boom")


def _app_config(outputs):
    return AppConfig(
        location=Location(1.0, 2.0),
        tracking=TrackingConfig("satellites_fly", "https://x", 10, 10, 1, 3600, 0.0),
        satellites=(),
        outputs=tuple(outputs),
    )


def test_file_output_appends_lines(tmp_path):
    path = str(tmp_path / "cmd.log")
    out = FileOutput(path, append=True)
    out.send("a")
    out.send("b")
    out.close()
    assert open(path, encoding="utf-8").read() == "a\nb\n"


def test_file_output_overwrite_mode(tmp_path):
    path = str(tmp_path / "cmd.log")
    first = FileOutput(path, append=False)
    first.send("first")
    first.close()
    second = FileOutput(path, append=False)
    second.send("second")
    second.close()
    assert open(path, encoding="utf-8").read() == "second\n"


def test_multi_fans_out_to_all():
    a, b = RecordingOutput(), RecordingOutput()
    MultiOutput((a, b)).send("cmd")
    assert a.sent == ["cmd"] and b.sent == ["cmd"]


def test_multi_isolates_a_failing_sink():
    good = RecordingOutput()
    out = MultiOutput((FailingOutput(), good))
    out.send("cmd")  # must not raise despite the failing sink
    assert good.sent == ["cmd"]


def test_multi_close_closes_all():
    a, b = RecordingOutput(), RecordingOutput()
    MultiOutput((a, b)).close()
    assert a.closed and b.closed


def test_tcp_send_is_graceful_without_listener():
    # Port 9 (discard) has no listener here -> connection refused.
    out = TcpOutput("127.0.0.1", 9, timeout=1.0)
    out.send("cmd")  # must not raise
    out.close()


def test_build_output_returns_multi():
    out = build_output(_app_config([OutputConfig(type="stdout")]))
    assert isinstance(out, MultiOutput)


def test_build_output_file_requires_path():
    with pytest.raises(ConfigError):
        build_output(_app_config([OutputConfig(type="file", path=None)]))


def test_build_output_rejects_unknown_type():
    with pytest.raises(ConfigError):
        build_output(_app_config([OutputConfig(type="mystery")]))
