import socket as stdlib_socket
from collections import deque
from typing import Union

from ..exceptions import LircdConnectionError, LircdSocketError
from .abstract_connection import AbstractConnection
from .default_connection import DefaultConnection


class LircdConnection(AbstractConnection):
    def __init__(
        self,
        address: Union[str, tuple] = DefaultConnection().address,
        socket: stdlib_socket.socket = DefaultConnection().socket,
        timeout: float = 5.0,
    ):
        self.__buffer = deque()
        self.__buffer_size = 4096
        self.__address = address
        self.__socket = socket
        self.__socket.settimeout(timeout)

    def connect(self):
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
    def socket(self) -> stdlib_socket.socket:
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
        except stdlib_socket.timeout:
            raise TimeoutError(
                "could not find any data on the socket after "
                f"{self.__socket.gettimeout()} seconds, socket timed out."
            )
        except stdlib_socket.error as error:
            raise LircdSocketError(
                f"An error occurred while reading from the lircd socket: {error}"
            )
