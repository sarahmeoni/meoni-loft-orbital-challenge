#
# config.py
#

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from models.app_config import AppConfig
from utils.errors import ConfigError


def load_config(path: str | Path) -> AppConfig:
    raw = _read_json(Path(path))
    if not isinstance(raw, dict):
        raise ConfigError("Top-level config must be a JSON object.")
    try:
        return AppConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(_describe(exc)) from exc


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config file is not valid JSON: {exc}") from exc


def _describe(exc: ValidationError) -> str:
    problems = "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )
    return f"invalid configuration: {problems}"
