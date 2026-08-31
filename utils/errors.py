#
# errors.py
#


class SatelliteLightingError(Exception):
    """Base class for all satellite-lighting errors."""


class ConfigError(SatelliteLightingError):
    """Raised when the configuration file is missing, malformed or invalid."""


class TrackingError(SatelliteLightingError):
    """Raised when a satellite-tracking backend fails to return usable data."""


class OutputError(SatelliteLightingError):
    """Raised when a command cannot be written to a configured output."""
