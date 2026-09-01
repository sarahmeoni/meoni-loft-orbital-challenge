#
# app_config.py
#

from dataclasses import dataclass

from models.location import Location
from models.output_config import OutputConfig
from models.satellite import Satellite
from models.tracking_config import TrackingConfig


@dataclass(frozen=True, slots=True)
class AppConfig:
    location: Location
    tracking: TrackingConfig
    satellites: tuple[Satellite, ...]
    outputs: tuple[OutputConfig, ...]
