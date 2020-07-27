import platform
import socket as system_socket
from collections import deque
from typing import Union

from ..exceptions import LircdConnectionError, LircdSocketError, LircdSocketTimeoutError
from .abstract_connection import AbstractConnection


class LircdConnection(AbstractConnection):
    def __init__(
        self,
        address: Union[str, tuple] = None,
        socket: system_socket.socket = None,
        timeout: float = 5.0,
    ):
        operating_system = platform.system().capitalize()

        self.__default_address = {
            "Linux": "/var/run/lirc/lircd",
            "Windows": ("localhost", 8765),
            "Darwin": "/opt/run/var/run/lirc/lircd",
        }
        self.__default_socket = {
            "Linux": system_socket.socket(
                system_socket.AF_UNIX, system_socket.SOCK_STREAM
            ),
            "Darwin": system_socket.socket(
                system_socket.AF_UNIX, system_socket.SOCK_STREAM
            ),
            "Windows": system_socket.socket(
                system_socket.AF_INET, system_socket.SOCK_STREAM
            ),
        }

        self.__buffer = deque()
        self.__buffer_size = 4096
        self.__socket = (
            socket if socket is not None else self.__default_socket[operating_system]
        )
        self.__address = (
            address if address is not None else self.__default_address[operating_system]
        )

        self.__socket.settimeout(timeout)

        try:
            self.__socket.connect(self.__address)
        except FileNotFoundError:
            raise LircdConnectionError(
                f"Could not connect to lircd at {self.__address} with socket "
                f"{self.__socket}. Did you start the `lircd` daemon?"
            )
        except Exception as error:
            raise LircdConnectionError(error)

    @property
    def socket(self) -> system_socket.socket:
        return self.__socket

    @property
    def address(self) -> str:
        return self.__address

    def close(self):
        self.__socket.close()

    def send(self, data: str):
        if not isinstance(data, str):
            raise TypeError("data parameter to send() must be a string")

        if not data.endswith("\n"):
            data += "\n"

        self.__socket.sendall(data.encode("utf-8"))

    def readline(self) -> str:
        if len(self.__buffer) >= 1:
            return self.__buffer.popleft()

        try:
            packet = self.__socket.recv(self.__buffer_size)

            if packet.endswith(b"\n"):
                packet = packet.strip()

            if b"\n" in packet:
                self.__buffer.extend(
                    line.decode("utf-8") for line in packet.split(b"\n")
                )
            else:
                self.__buffer.append(packet.decode("utf-8"))

            return self.__buffer.popleft()
        except system_socket.timeout:
            raise LircdSocketTimeoutError(
                "could not find any data on the socket after "
                f"{self.__socket.gettimeout()} seconds, socket timed out."
            )
        except system_socket.error as error:
            raise LircdSocketError(
                f"An error occurred while reading from the lircd socket: {error}"
            )
