import socket
from enum import Enum


class DefaultSocket(Enum):
    """
    Default socket to use for the lircd socket, depending
    on the operating system.
    """

    LINUX = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    DARWIN = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    WINDOWS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
