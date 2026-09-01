#
# base.py
#

from abc import ABC, abstractmethod
from datetime import datetime


class SatelliteTracker(ABC):

    @abstractmethod
    def satellites_overhead(self, now: datetime) -> set[int]:
        # Return the NORAD ids
        raise NotImplementedError
