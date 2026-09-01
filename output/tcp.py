#
# tcp.py
#

import logging
import socket

from output.base import Output

logger = logging.getLogger(__name__)


class TcpOutput(Output):

    def __init__(self, host: str, port: int, timeout: float = 10.0) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._socket: socket.socket | None = None

    def send(self, command: str) -> None:
        try:
            self._ensure_connected()
            assert self._socket is not None
            self._socket.sendall(f"{command}\n".encode())
        except OSError as exc:
            logger.warning("TCP send to %s:%s failed: %s", self._host, self._port, exc)
            self._reset()

    def _ensure_connected(self) -> None:
        if self._socket is None:
            self._socket = socket.create_connection((self._host, self._port), self._timeout)

    def _reset(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def close(self) -> None:
        self._reset()
