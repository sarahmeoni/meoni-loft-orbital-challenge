#
# stdout.py
#

import sys

from output.base import Output


class StdoutOutput(Output):

    def send(self, command: str) -> None:
        sys.stdout.write(f"{command}\n")
        sys.stdout.flush()
