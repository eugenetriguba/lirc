import platform
import socket
import threading
from itertools import islice
from typing import List, Union

from lirc.exceptions import (
    InvalidReplyPacketFormatError,
    LircCommandFailureError,
    LircSocketError,
    LircSocketTimeoutError,
)
from lirc.lirc_response import LircResponse

DEFAULT_ADDRESS_LINUX = "/var/run/lirc/lircd"
DEFAULT_ADDRESS_WINDOWS = ("localhost", 8765)
DEFAULT_ADDRESS_DARWIN = "/opt/run/var/run/lirc/lircd"


class Lirc:
    """Communicate with the lircd daemon."""

    def __init__(
        self,
        address: Union[str, tuple] = None,
        socket: socket.socket = None,
        timeout: float = 5.0,
    ) -> None:
        """
        Initialize Lirc by connecting to the lircd socket.

        :param address: The address to lircd. The default address
            depends on the operating system you are using. On Linux,
            it is "/var/run/lirc/lircd". On macOS, it is
            "/opt/run/var/run/lirc/lircd". And on Windows, it is
            ("localhost", 8765) to connect to localhost:8765, which
            is the default address for WinLIRC.

        :param socket: The socket.socket used to connect to the lircd socket.

        :param timeout: The amount of time in seconds to wait before timing out when
            receiving data from the lirc server.

        :raises FileNotFoundError: If the socket cannot connect to the address.
        """
        self.__lock = threading.Lock()
        self.__encoding = "utf-8"
        self.__timeout = timeout
        self.__socket = self.__determine_socket(socket)
        self.__address = (
            address
            if address is not None
            else globals()[f"DEFAULT_ADDRESS_{platform.system().upper()}"]
        )

        self.__socket.settimeout(self.__timeout)
        self.__socket.connect(self.__address)

    @staticmethod
    def __determine_socket(lircd_socket: Union[socket.socket, None]) -> socket.socket:
        """
        Determines the default socket type to be used based on the
        operating system of the host if no socket to use is provided.

        It will use a socket configured for TCP on Windows (since
        that is how WinLIRC works), and it will default to a socket
        configured for unix sockets otherwise (Darwin & Linux).

        :param lircd_socket: The socket passed in to the Lirc constructor.
        """
        if lircd_socket:
            return lircd_socket

        if platform.system() == "Windows":
            return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            return socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def __send_command(self, command: str) -> LircResponse:
        """
        Send a command to lircd.

        :param command: A command from the lircd socket command interface.
        See SOCKET COMMAND INTERFACE in https://www.lirc.org/html/lircd.html
        for more information.

        :return: a response object containing information on the command sent.
        """
        if not command.endswith("\n"):
            command += "\n"

        try:
            self.__lock.acquire()
            self.__socket.sendall(command.encode(self.__encoding))

            reply_packet = self.__read_reply_packet()
            return self.__parse_reply_packet(reply_packet)
        finally:
            self.__lock.release()

    def __read_reply_packet(self) -> str:
        """
        Read the reply packet that lircd sends after a sent command.

        Reply packet format:

            BEGIN
            <command>
            [SUCCESS|ERROR]
            [DATA
            n
            n lines of data]
            END

        :return: The contents of the reply packet from BEGIN to END.

        :raises LircSocketTimeoutError: If recv does not find any data after
            the specified timeout amount of seconds.
        :raises LircSocketError: If something else went wrong with the socket.
        """
        try:
            BUFFER_LENGTH = 256
            buffer = ""
            data = self.__socket.recv(BUFFER_LENGTH)

            # Ignore recieve requests that the socket caches
            while "BEGIN" not in data.decode(self.__encoding):
                data = self.__socket.recv(BUFFER_LENGTH)

            buffer += data.decode(self.__encoding)

            while not buffer.endswith("END\n"):
                data = self.__socket.recv(BUFFER_LENGTH)
                buffer += data.decode(self.__encoding)

            return buffer
        except (socket.timeout, socket.error) as error:
            if len(error.args) >= 1 and error.args[0] == "timed out":
                raise LircSocketTimeoutError(
                    f"could not find any data on the socket after "
                    f"{self.__timeout} seconds, socket timed out."
                )
            else:
                raise LircSocketError(error)

    def __parse_reply_packet(self, packet: str) -> LircResponse:
        """
        Parse the reply packet from lircd.

        :param packet: The reply packet from lirc.

        :return: a response object containing information on the command sent.
        :raises LircCommandFailureError: If the command we send to LIRC fails.
            The data from the response of the command, likey the error message,
            is used as the message.
        """
        lines = packet.split("\n")
        current_index = 0
        response = LircResponse("", [])

        if lines[current_index] == "BEGIN":
            current_index += 1
        else:
            return response

        response.command = lines[current_index]
        current_index += 1

        command_success = True if lines[current_index] == "SUCCESS" else False
        current_index += 1

        if lines[current_index] == "END":
            return response
        elif lines[current_index] == "DATA":
            current_index += 1
            data_length = int(lines[current_index])
            current_index += 1
        else:
            raise InvalidReplyPacketFormatError(
                f"Unknown format for reply packet: \n{lines}"
            )

        for line in islice(lines, current_index, current_index + data_length):
            response.data.append(line)

        if not command_success:
            raise LircCommandFailureError(response.data)

        return response

    def send_once(
        self, key: str, remote: str, repeat_count: int = 1
    ) -> Union[LircResponse, List[LircResponse]]:
        """
        Send an LIRC SEND_ONCE command.

        Structure of the command:
          * SEND_ONCE <remote-name> <key-name-from-remote-file> [repeat-count]

        :param key: The name of the key to send.
        :param remote: The remote to use keys from.
        :param repeat_count: The number of times to press this key.

        :return: a response from the command or a list of those responses
            if repeat_count > 1.
        """
        # The reason the optional repeat-count parameter isn't used in this
        # implementaiton is because we want to be able to store all the
        # responses from each command.
        if repeat_count > 1:
            responses = []

            while repeat_count > 0:
                responses.append(self.__send_command(f"SEND_ONCE {remote} {key}"))
                repeat_count -= 1

            return responses

        return self.__send_command(f"SEND_ONCE {remote} {key}")

    def send_start(self, key: str, remote: str) -> LircResponse:
        """
        Send an LIRC SEND_START command.

        Structure of the command:
          * SEND_START <remote-name> <key-name-from-remote-file>

        :param key: The name of the key to start sending.
        :param remote: The remote to use keys from.

        :return: The response of the command.
        """
        return self.__send_command(f"SEND_START {remote} {key}")

    def send_stop(self, key: str, remote: str) -> LircResponse:
        """
        Send an LIRC SEND_STOP command.

        Structure of the command:
          * SEND_STOP <remote-name> <key-name-from-remote-file>

        :param key: The name of the key to start sending.
        :param remote: The remote to use keys from.

        :return: The response of the command.
        """
        return self.__send_command(f"SEND_STOP")

    def list_remotes(self) -> LircResponse:
        """
        List all the remotes in LIRC

        :return: The response of the command.
        """
        return self.__send_command("LIST")

    def list_remote_keys(self, remote: str) -> LircResponse:
        """
        List all the keys for a specific remote.

        :param remote: The remote to list the keys of.

        :return: The response of the command.
        """
        return self.__send_command(f"LIST {remote}")

    def set_inputlog(self, path: str) -> LircResponse:
        """
        Set the path to log all lircd received data to.

        :return: The response of the command.
        """
        return self.__send_command(f"SET_INPUTLOG {path}")

    def stop_inputlog(self) -> LircResponse:
        """
        Stop logging to the inputlog path from set_inputlog.

        :return: The response of the command.
        """
        # When calling SET_INPUTLOG without the path argument,
        # it will stop logging and close the logfile.
        return self.__send_command("SET_INPUTLOG")

    def version(self) -> LircResponse:
        """
        Retrieve the version of LIRC

        :return: The response of the command with
            the version in the data field.
        """
        return self.__send_command("VERSION")
