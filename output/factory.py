#
# factory.py
#

from models.app_config import AppConfig
from models.output_config import (
    FileOutputConfig,
    OutputConfig,
    StdoutOutputConfig,
    TcpOutputConfig,
)
from output.base import Output
from output.file import FileOutput
from output.multi import MultiOutput
from output.stdout import StdoutOutput
from output.tcp import TcpOutput
from utils.errors import ConfigError


def build_output(config: AppConfig) -> Output:
    return MultiOutput(tuple(_build_one(item, config) for item in config.outputs))


def _build_one(item: OutputConfig, config: AppConfig) -> Output:
    if isinstance(item, StdoutOutputConfig):
        return StdoutOutput()
    if isinstance(item, FileOutputConfig):
        return FileOutput(path=item.path, append=item.append)
    if isinstance(item, TcpOutputConfig):
        return TcpOutput(
            host=item.host,
            port=item.port,
            timeout=config.tracking.request_timeout_seconds,
        )
    raise ConfigError(f"Unsupported output type '{item!r}'.")
