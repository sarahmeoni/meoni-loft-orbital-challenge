#
# config.py
#

import json
from pathlib import Path
from typing import Any

from models.app_config import AppConfig
from models.location import Location
from models.output_config import OutputConfig
from models.satellite import Satellite
from models.tracking_config import TrackingConfig
from utils.const import Constants
from utils.errors import ConfigError


def load_config(path: str | Path) -> AppConfig:
    """Read, validate and return the application configuration at ``path``."""
    raw = _read_json(Path(path))
    if not isinstance(raw, dict):
        raise ConfigError("Top-level config must be a JSON object.")
    return AppConfig(
        location=_parse_location(_require_key(raw, "location", dict)),
        tracking=_parse_tracking(raw.get("tracking", {})),
        satellites=_parse_satellites(_require_key(raw, "satellites", list)),
        outputs=_parse_outputs(_require_key(raw, "outputs", list)),
    )


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config file is not valid JSON: {exc}") from exc


def _parse_location(data: dict[str, Any]) -> Location:
    lat = _require_number(data, "latitude", "location")
    lon = _require_number(data, "longitude", "location")
    _require_in_range(lat, Constants.min_latitude, Constants.max_latitude, "location.latitude")
    _require_in_range(lon, Constants.min_longitude, Constants.max_longitude, "location.longitude")
    return Location(latitude=lat, longitude=lon, name=_optional_str(data, "name", "location"))


def _parse_tracking(data: dict[str, Any]) -> TrackingConfig:
    if not isinstance(data, dict):
        raise ConfigError("'tracking' must be a JSON object.")
    backend = data.get("backend", Constants.default_backend)
    if backend not in Constants.supported_backends:
        raise ConfigError(
            f"Unsupported tracking backend '{backend}'. "
            f"Supported: {', '.join(Constants.supported_backends)}."
        )
    return TrackingConfig(
        backend=backend,
        api_base_url=data.get("api_base_url", Constants.default_api_base_url),
        poll_interval_seconds=_require_positive_int(
            data, "poll_interval_seconds", Constants.default_poll_interval_seconds
        ),
        request_timeout_seconds=_require_positive_int(
            data, "request_timeout_seconds", Constants.default_request_timeout_seconds
        ),
        passes_lookahead_days=_require_positive_int(
            data, "passes_lookahead_days", Constants.default_passes_lookahead_days
        ),
        refresh_interval_seconds=_require_positive_int(
            data, "refresh_interval_seconds", Constants.default_refresh_interval_seconds
        ),
        min_culmination_degrees=float(
            data.get("min_culmination_degrees", Constants.default_min_culmination_degrees)
        ),
    )


def _parse_satellites(items: list[Any]) -> tuple[Satellite, ...]:
    if not items:
        raise ConfigError("'satellites' must contain at least one satellite.")
    satellites: list[Satellite] = []
    seen: set[int] = set()
    for index, item in enumerate(items):
        ctx = f"satellites[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{ctx} must be a JSON object.")
        norad_id = _require_int(item, "norad_id", ctx)
        if norad_id in seen:
            raise ConfigError(f"Duplicate norad_id {norad_id} in 'satellites'.")
        seen.add(norad_id)
        color = _require_non_empty_str(item, "color", ctx)
        satellites.append(
            Satellite(norad_id=norad_id, color=color, name=_optional_str(item, "name", ctx))
        )
    return tuple(satellites)


def _parse_outputs(items: list[Any]) -> tuple[OutputConfig, ...]:
    if not items:
        raise ConfigError("'outputs' must contain at least one output.")
    outputs: list[OutputConfig] = []
    for index, item in enumerate(items):
        ctx = f"outputs[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{ctx} must be a JSON object.")
        out_type = _require_non_empty_str(item, "type", ctx)
        if out_type not in Constants.supported_output_types:
            raise ConfigError(
                f"{ctx}: unsupported output type '{out_type}'. "
                f"Supported: {', '.join(Constants.supported_output_types)}."
            )
        if out_type == Constants.output_file:
            outputs.append(
                OutputConfig(
                    type=out_type,
                    path=_require_non_empty_str(item, "path", ctx),
                    append=bool(item.get("append", Constants.default_file_append)),
                )
            )
        elif out_type == Constants.output_tcp:
            outputs.append(
                OutputConfig(
                    type=out_type,
                    host=_require_non_empty_str(item, "host", ctx),
                    port=_require_int(item, "port", ctx),
                )
            )
        else:
            outputs.append(OutputConfig(type=out_type))
    return tuple(outputs)


def _require_key(data: dict[str, Any], key: str, expected: type) -> Any:
    if key not in data:
        raise ConfigError(f"Missing required config key: '{key}'.")
    value = data[key]
    if not isinstance(value, expected):
        raise ConfigError(f"Config key '{key}' must be a {expected.__name__}.")
    return value


def _require_number(data: dict[str, Any], key: str, ctx: str) -> float:
    value = data.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigError(f"{ctx}.{key} must be a number.")
    return float(value)


def _require_int(data: dict[str, Any], key: str, ctx: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(f"{ctx}.{key} must be an integer.")
    return value


def _require_non_empty_str(data: dict[str, Any], key: str, ctx: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{ctx}.{key} must be a non-empty string.")
    return value


def _optional_str(data: dict[str, Any], key: str, ctx: str) -> str | None:
    if key not in data or data[key] is None:
        return None
    return _require_non_empty_str(data, key, ctx)


def _require_positive_int(data: dict[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigError(f"tracking.{key} must be a positive integer.")
    return value


def _require_in_range(value: float, low: float, high: float, ctx: str) -> None:
    if not low <= value <= high:
        raise ConfigError(f"{ctx} must be between {low} and {high}.")
