import socket
from collections import deque
from typing import Union

from ..exceptions import LircdConnectionError, LircdSocketError
from .abstract_connection import AbstractConnection
from .default_connection import DefaultConnection


class LircdConnection(AbstractConnection):
    def __init__(
        self,
        address: Union[str, tuple] = None,
        socket: socket.socket = None,
        timeout: float = 5.0,
    ):
        """
        Initialize the LircdConnection. This sets up state we'll
        need, but it does not connect to that socket. To connect,
        we can call connect() after initialization.

        Args:
            address: The address to the socket. Defaults to different
                values depending on the host operating system. On Linux,
                it defaults to ``/var/run/lirc/lircd``. On Windows, a tuple
                of ``("localhost", 8765)``. And on Darwin (macOS),
                ``/opt/local/var/run/lirc/lircd``.

            socket: The socket to use to connect to lircd. The default
                socket is determined using the host operating system. For
                Linux and Darwin, a unix domain socket connection is used
                i.e. ``socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)``.
                However on Windows, a TCP socket is used
                i.e. ``socket.socket(socket.AF_INET, socket.SOCK_STREAM)``.

            timeout: The amount of time to wait for data from the socket before
                we timeout.
        """
        default = DefaultConnection()

        if address is None:
            address = default.address

        if socket is None:
            socket = default.socket

        self.__buffer = deque()
        self.__buffer_size = 4096
        self.__address = address
        self.__socket = socket
        self.__socket.settimeout(timeout)

    def connect(self):
        """
        Connect to the socket at the address both specified on init.

        Raises:
            LircdConnectionError: If the address is invalid or lircd
                is not running.
        """
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
    def address(self) -> str:
        """
        Retrieve the address that this lircd connection
        is connected to.

        Returns:
            The current address being used.
        """
        return self.__address

    def close(self):
        """
        Closes the socket connection.
        """
        self.__socket.close()

    def send(self, data: str):
        """
        Send a commend to the lircd socket connection.

        Args:
            data: The data to send to the lircd socket.

        Raises:
            TypeError: if data is not a string.
        """
        if not isinstance(data, str):
            raise TypeError("data parameter to send() must be a string")

        if not data.endswith("\n"):
            data += "\n"

        self.__socket.sendall(data.encode("utf-8"))

    def readline(self) -> str:
        """
        Read a line of data from the lircd socket.

        We read 4096 bytes at a time as the buffer size.
        Therefore after data is read from the socket, all
        the lines are stored in a buffer if there is more than
        1 and subsequent calls grab a line that stored in that
        buffer until it is empty. Then, another call to the
        socket would be made.

        Raises:
            TimeoutError: If we are not able to grab data from
                the socket in a specified amount of time (the initial
                timeout time on initialization).

            LircdSocketError: If some other error happened when
                trying to read from the socket.

        Returns:
            A line from the lircd socket.
        """
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
        except socket.timeout:
            raise TimeoutError(
                "could not find any data on the socket after "
                f"{self.__socket.gettimeout()} seconds, socket timed out."
            )
        except socket.error as error:
            raise LircdSocketError(
                f"An error occurred while reading from the lircd socket: {error}"
            )
