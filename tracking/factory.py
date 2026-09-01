#
# factory.py
#

import requests

from models.app_config import AppConfig
from tracking.base import SatelliteTracker
from tracking.fly import FlyDevTracker
from utils.const import Constants
from utils.errors import ConfigError


def build_tracker(
    config: AppConfig, session: requests.Session | None = None
) -> SatelliteTracker:
    backend = config.tracking.backend
    if backend == Constants.backend_satellites_fly:
        return FlyDevTracker(
            location=config.location,
            satellites=config.satellites,
            config=config.tracking,
            session=session,
        )
    raise ConfigError(f"Unsupported tracking backend '{backend}'.")
