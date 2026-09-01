#
# app_config.py
#

from pydantic import BaseModel, ConfigDict, Field, field_validator
from models.location import Location
from models.output_config import OutputConfig, StdoutOutputConfig
from models.satellite import Satellite
from models.tracking_config import TrackingConfig


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    location: Location
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    satellites: tuple[Satellite, ...] = Field(min_length=1)
    outputs: tuple[OutputConfig, ...] = Field(
        default=(StdoutOutputConfig(),), min_length=1
    )

    @field_validator("satellites")
    @classmethod
    def _unique_norad_ids(cls, value: tuple[Satellite, ...]) -> tuple[Satellite, ...]:
        ids = [sat.norad_id for sat in value]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate norad_id in 'satellites'.")
        return value
