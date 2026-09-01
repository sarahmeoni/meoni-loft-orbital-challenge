#
# output_config.py
#

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field
from utils.const import Constants


class StdoutOutputConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["stdout"] = "stdout"


class FileOutputConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["file"] = "file"
    path: str = Field(min_length=1)
    append: bool = Constants.default_file_append


class TcpOutputConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["tcp"] = "tcp"
    host: str = Field(min_length=1)
    port: int = Field(strict=True, gt=0)


# Discriminated on ``type`` so each variant enforces its own required fields.
OutputConfig = Annotated[
    StdoutOutputConfig | FileOutputConfig | TcpOutputConfig,
    Field(discriminator="type"),
]
