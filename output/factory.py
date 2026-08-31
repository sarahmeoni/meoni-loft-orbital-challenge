#
# factory.py
#

from models.app_config import AppConfig
from models.output_config import OutputConfig
from output.base import Output
from output.file import FileOutput
from output.multi import MultiOutput
from output.stdout import StdoutOutput
from output.tcp import TcpOutput
from utils.const import Constants
from utils.errors import ConfigError


def build_output(config: AppConfig) -> Output:
    """Build a single fan-out Output from the configured sinks."""
    return MultiOutput(tuple(_build_one(item, config) for item in config.outputs))


def _build_one(item: OutputConfig, config: AppConfig) -> Output:
    if item.type == Constants.output_stdout:
        return StdoutOutput()
    if item.type == Constants.output_file:
        if item.path is None:
            raise ConfigError("file output requires 'path'.")
        return FileOutput(path=item.path, append=item.append)
    if item.type == Constants.output_tcp:
        if item.host is None or item.port is None:
            raise ConfigError("tcp output requires 'host' and 'port'.")
        return TcpOutput(
            host=item.host,
            port=item.port,
            timeout=config.tracking.request_timeout_seconds,
        )
    raise ConfigError(f"Unsupported output type '{item.type}'.")
