import platform
import socket as system_socket
from collections import deque
from typing import Union

from ..exceptions import LircdConnectionError, LircdSocketError, LircdSocketTimeoutError
from .abstract_connection import AbstractConnection
from .default_address import DefaultAddress
from .default_socket import DefaultSocket


class LircdConnection(AbstractConnection):
    def __init__(
        self,
        address: Union[str, tuple] = None,
        socket: system_socket.socket = None,
        timeout: float = 5.0,
    ):
        """
        Initialize the connection by connecting to the lircd socket.

        The default address depends on the operating system
        you are using. On Linux, it is "/var/run/lirc/lircd".
        On macOS, it is "/opt/run/var/run/lirc/lircd". And on
        Windows, it is ("localhost", 8765) to connect to localhost:8765,
        which is the default address for WinLIRC.

        The socket is also determined for you if one is not provided. A unix
        domain socket is connected to on macOS and Linux. A TCP socket
        is used for Windows.

        Args:
            address: The address to lircd, determined for you if
            one is not provided.

            socket: The socket.socket used to connect to the lircd socket.

            timeout: The amount of time in seconds to wait before timing out when
            receiving data from lircd

        Raises:
             LircConnectionError: If the socket cannot connect to the address.
        """
        operating_system = platform.system().upper()

        self.__buffer = deque()
        self.__buffer_size = 4096
        self.__socket = (
            socket if socket is not None else DefaultSocket[operating_system].value
        )
        self.__address = (
            address if address is not None else DefaultAddress[operating_system].value
        )

        self.__socket.settimeout(timeout)

        try:
            self.__socket.connect(self.__address)
        except FileNotFoundError:
            raise LircdConnectionError(
                f"Could not connect to lircd at {self.__address} with socket "
                f"{self.__socket}. Did you start the `lircd` daemon?"
            )

    @property
    def socket(self) -> system_socket.socket:
        return self.__socket

    @property
    def address(self) -> str:
        return self.__address

    def close(self):
        self.__socket.close()

    def send(self, data: str):
        if not data.endswith("\n"):
            data += "\n"

        self.__socket.sendall(data.encode("utf-8"))

    def readline(self) -> str:
        """
        Read the reply packet that is on the socket after a
        command is sent to lircd.

        Raises:
            LircdSocketTimeoutError: If recv does not find any data after
            the specified timeout amount of seconds (called without a command
            being sent?).

            LircdSocketError: If something else went wrong with the socket.
        """
        if len(self.__buffer) >= 1:
            return self.__buffer.popleft()

        try:
            packet = self.__socket.recv(self.__buffer_size)

            if b"\n" in packet:
                for line in packet.split(b"\n"):
                    self.__buffer.append(line.decode("utf-8"))
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
