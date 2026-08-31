#
# base.py
#

from abc import ABC, abstractmethod
from datetime import datetime


class SatelliteTracker(ABC):
    """Interface for backends that report which satellites are overhead.

    Implementations decide how to source pass data; the service only ever
    asks the question below, so backends stay swappable via configuration.
    """

    @abstractmethod
    def satellites_overhead(self, now: datetime) -> set[int]:
        """Return the NORAD ids passing over the configured location at ``now``."""
        raise NotImplementedError
