#
# file.py
#

from output.base import Output


class FileOutput(Output):
    """Append (or overwrite) commands to a file, one per line."""

    def __init__(self, path: str, append: bool = True) -> None:
        self._handle = open(path, "a" if append else "w", encoding="utf-8")

    def send(self, command: str) -> None:
        self._handle.write(f"{command}\n")
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()
