#
# multi.py
#

import logging

from output.base import Output

logger = logging.getLogger(__name__)


class MultiOutput(Output):

    def __init__(self, outputs: tuple[Output, ...]) -> None:
        self._outputs = outputs

    def send(self, command: str) -> None:
        for output in self._outputs:
            try:
                output.send(command)
            except Exception as exc:
                # One misbehaving sink must not stop the others.
                logger.warning("Output %s failed: %s", type(output).__name__, exc)

    def close(self) -> None:
        for output in self._outputs:
            output.close()
