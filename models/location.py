#
# location.py
#

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Location:
    latitude: float
    longitude: float
    name: str | None = None
