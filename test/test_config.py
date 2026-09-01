#
# test_config.py
#
# Validation behaviour of utils.config.load_config.
#

import json

import pytest

from utils.config import load_config
from utils.errors import ConfigError


def _write(tmp_path, data):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _valid():
    return {
        "location": {"name": "Lab", "latitude": 39.7, "longitude": -105.2},
        "satellites": [{"norad_id": 25544, "color": "blue"}],
        "outputs": [{"type": "stdout"}],
    }


def test_valid_config_loads_with_tracking_defaults(tmp_path):
    cfg = load_config(_write(tmp_path, _valid()))
    assert cfg.location.name == "Lab"
    assert cfg.satellites[0].norad_id == 25544
    assert cfg.outputs[0].type == "stdout"
    # tracking block omitted -> defaults applied
    assert cfg.tracking.backend == "satellites_fly"
    assert cfg.tracking.poll_interval_seconds == 10
    assert cfg.tracking.refresh_interval_seconds == 3600


def test_missing_required_key_raises(tmp_path):
    data = _valid()
    del data["satellites"]
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_outputs_optional_defaults_to_stdout(tmp_path):
    data = _valid()
    del data["outputs"]
    cfg = load_config(_write(tmp_path, data))
    assert len(cfg.outputs) == 1
    assert cfg.outputs[0].type == "stdout"


def test_latitude_out_of_range_raises(tmp_path):
    data = _valid()
    data["location"]["latitude"] = 200.0
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_duplicate_norad_id_raises(tmp_path):
    data = _valid()
    data["satellites"] = [
        {"norad_id": 1, "color": "blue"},
        {"norad_id": 1, "color": "pink"},
    ]
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_empty_satellites_raises(tmp_path):
    data = _valid()
    data["satellites"] = []
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_unsupported_backend_raises(tmp_path):
    data = _valid()
    data["tracking"] = {"backend": "nope"}
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_unsupported_output_type_raises(tmp_path):
    data = _valid()
    data["outputs"] = [{"type": "carrier_pigeon"}]
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_file_output_requires_path(tmp_path):
    data = _valid()
    data["outputs"] = [{"type": "file"}]
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_tcp_output_requires_host_and_port(tmp_path):
    data = _valid()
    data["outputs"] = [{"type": "tcp", "host": "127.0.0.1"}]
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, data))


def test_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError):
        load_config(tmp_path / "does_not_exist.json")


def test_invalid_json_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
