#
# output_config.py
#

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OutputConfig:
    """A single command sink. Which fields apply depends on ``type``."""

    type: str
    path: str | None = None
    append: bool = True
    host: str | None = None
    port: int | None = None
