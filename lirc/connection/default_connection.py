import platform
import socket
from typing import Tuple, Union


class DefaultConnection:
    def __init__(self):
        """
        This class provides our operating specific default
        connection parameters.
        """
        self.__operating_system = platform.system().capitalize()

    @property
    def socket(self) -> socket.socket:
        """
        Retreives the default socket that should be used
        for lircd on the current operating system.

        Returns:
            A socket.socket setup correctly for the current OS.
        """
        if self.__operating_system == "Linux" or self.__operating_system == "Darwin":
            return socket.socket(
                socket.AF_UNIX, socket.SOCK_STREAM
            )

        if self.__operating_system == "Windows":
            return socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )

    @property
    def address(self) -> Union[str, Tuple[str, int]]:
        """
        Retrieves the default address that should be used
        for lircd on the current operating system.

        Returns:
            A str path to the lircd socket on the file system
            if on Linux or MacOS; a Tuple of the address and port
            if on Windows.
        """
        return {
            "Linux": "/var/run/lirc/lircd",
            "Windows": ("localhost", 8765),
            "Darwin": "/opt/run/var/run/lirc/lircd",
        }[self.__operating_system]
