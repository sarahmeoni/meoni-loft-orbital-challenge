#
# satellite.py
#

from pydantic import BaseModel, ConfigDict, Field

class Satellite(BaseModel):
    model_config = ConfigDict(frozen=True)

    norad_id: int = Field(strict=True, gt=0)
    color: str = Field(min_length=1)
    name: str | None = Field(default=None, min_length=1)
