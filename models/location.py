#
# location.py
#

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Location:
    """The lab whose sky we are watching."""

    latitude: float
    longitude: float
    name: str | None = None
