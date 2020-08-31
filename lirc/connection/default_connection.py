import platform
import socket as stdlib_socket
from typing import Tuple, Union


class DefaultConnection:
    def __init__(self):
        self.__operating_system = platform.system().capitalize()

    @property
    def socket(self) -> stdlib_socket.socket:
        unix_socket = stdlib_socket.socket(
            stdlib_socket.AF_UNIX, stdlib_socket.SOCK_STREAM
        )
        tcp_socket = stdlib_socket.socket(
            stdlib_socket.AF_INET, stdlib_socket.SOCK_STREAM
        )

        return {"Linux": unix_socket, "Darwin": unix_socket, "Windows": tcp_socket}[
            self.__operating_system
        ]

    @property
    def address(self) -> Union[str, Tuple[str, int]]:
        return {
            "Linux": "/var/run/lirc/lircd",
            "Windows": ("localhost", 8765),
            "Darwin": "/opt/run/var/run/lirc/lircd",
        }[self.__operating_system]
