#
# stdout.py
#

import sys

from output.base import Output


class StdoutOutput(Output):
    """Write commands to standard output (one per line)."""

    def send(self, command: str) -> None:
        sys.stdout.write(f"{command}\n")
        sys.stdout.flush()
