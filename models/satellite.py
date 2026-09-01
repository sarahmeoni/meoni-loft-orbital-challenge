#
# satellite.py
#

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Satellite:
    norad_id: int
    color: str
    name: str | None = None
