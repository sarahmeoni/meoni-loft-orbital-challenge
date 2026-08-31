#
# satellite.py
#

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Satellite:
    """A satellite to track, mapped to the color its pass should show."""

    norad_id: int
    color: str
    name: str | None = None
