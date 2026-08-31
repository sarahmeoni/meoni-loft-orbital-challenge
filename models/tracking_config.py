#
# tracking_config.py
#

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrackingConfig:
    """How and how often to query the tracking backend."""

    backend: str
    api_base_url: str
    poll_interval_seconds: int
    request_timeout_seconds: int
    passes_lookahead_days: int
    refresh_interval_seconds: int
    min_culmination_degrees: float
