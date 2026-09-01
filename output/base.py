#
# base.py
#

from abc import ABC, abstractmethod


class Output(ABC):
    # A destination that receives formatted lighting commands.

    @abstractmethod
    def send(self, command: str) -> None:
        """Write a single command line to the destination."""
        raise NotImplementedError

    def close(self) -> None:
        """Release any resources held by the sink. Default is a no-op."""
