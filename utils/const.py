#
# const.py
#


class Constants:
    """Default values and fixed strings for the satellite-lighting service."""

    # Supported tracking backends
    backend_satellites_fly = "satellites_fly"
    supported_backends = (backend_satellites_fly,)

    # Tracking defaults (used when a field is omitted from the config)
    default_backend = backend_satellites_fly
    default_api_base_url = "https://satellites.fly.dev"
    default_poll_interval_seconds = 10
    default_request_timeout_seconds = 10
    default_passes_lookahead_days = 1
    default_refresh_interval_seconds = 3600
    default_min_culmination_degrees = 0.0

    # Supported output types
    output_stdout = "stdout"
    output_file = "file"
    output_tcp = "tcp"
    supported_output_types = (output_stdout, output_file, output_tcp)

    # File output default
    default_file_append = True

    # Command formatting: "25544: blue, 48915: pink"
    command_kv_separator = ": "
    command_pair_separator = ", "

    # Coordinate bounds (decimal degrees)
    min_latitude = -90.0
    max_latitude = 90.0
    min_longitude = -180.0
    max_longitude = 180.0
