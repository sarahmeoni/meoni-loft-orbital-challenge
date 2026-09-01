#
# tracking_config.py
#

from pydantic import BaseModel, ConfigDict, Field, field_validator
from utils.const import Constants


class TrackingConfig(BaseModel):
    # How and how often to query the tracking backend.
    model_config = ConfigDict(frozen=True)

    backend: str = Constants.default_backend
    api_base_url: str = Field(default=Constants.default_api_base_url, min_length=1)
    poll_interval_seconds: int = Field(
        default=Constants.default_poll_interval_seconds, strict=True, gt=0
    )
    request_timeout_seconds: int = Field(
        default=Constants.default_request_timeout_seconds, strict=True, gt=0
    )
    passes_lookahead_days: int = Field(
        default=Constants.default_passes_lookahead_days, strict=True, gt=0
    )
    refresh_interval_seconds: int = Field(
        default=Constants.default_refresh_interval_seconds, strict=True, gt=0
    )
    min_culmination_degrees: float = Field(
        default=Constants.default_min_culmination_degrees, strict=True
    )

    @field_validator("backend")
    @classmethod
    def _supported_backend(cls, value: str) -> str:
        if value not in Constants.supported_backends:
            raise ValueError(
                f"unsupported tracking backend '{value}'. "
                f"Supported: {', '.join(Constants.supported_backends)}."
            )
        return value
