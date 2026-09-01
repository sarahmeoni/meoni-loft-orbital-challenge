#
# location.py
#

from pydantic import BaseModel, ConfigDict, Field
from utils.const import Constants


class Location(BaseModel):
    model_config = ConfigDict(frozen=True)

    latitude: float = Field(strict=True, ge=Constants.min_latitude, le=Constants.max_latitude)
    longitude: float = Field(
        strict=True, ge=Constants.min_longitude, le=Constants.max_longitude
    )
    name: str | None = Field(default=None, min_length=1)
