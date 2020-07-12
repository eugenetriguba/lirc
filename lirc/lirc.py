import socket
import threading
from itertools import islice

from lirc.exceptions import (
    InvalidReplyPacketFormat,
    LircSocketError,
    LircSocketTimeoutError,
)
from lirc.response import LircResponse


class Lirc:
    """
    Communicate with the lircd daemon.

    More information on the lircd daemon, socket interface,
    reply packet format, etc. can be found at https://www.lirc.org/html/lircd.html
    That information is not all documented here because it would introduce
    a lot of repetitiveness in the docstrings.

    Example Usage:

        from lirc import Lirc

        lirc = Lirc()
        response = lirc.version()

        print(response.command)
        >>> 'VERSION'
        print(response.success)
        >>> True
        print(response.data)
        >>> ['0.10.1']
    """

    DEFAULT_SOCKET_PATH = "/var/run/lirc/lircd"
    ENCODING = "utf-8"

    def __init__(
        self,
        socket_path: str = DEFAULT_SOCKET_PATH,
        socket: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
        socket_timeout: int = 5,
    ) -> None:
        """
        Initialize Lirc by connecting to the lircd socket.

        :param socket_path: The path to the lircd socket.
        :param socket: The socket.socket used to connect to the lircd socket.
        """
        self.__lock = threading.Lock()
        self.__socket = socket
        self.__socket_timeout = socket_timeout
        self.__socket.settimeout(self.__socket_timeout)
        self.__socket.connect(socket_path)

    def __send_command(self, command: str) -> LircResponse:
        """
        Send a command to lircd.

        :param command: A command from the lircd socket command interface.
        See SOCKET COMMAND INTERFACE in https://www.lirc.org/html/lircd.html
        for more information.

        :return: A LircResponse containing information on the command sent,
            whether it was successful, and any other data, if any was sent.
        """
        if not command.endswith("\n"):
            command += "\n"

        try:
            self.__lock.acquire()
            self.__socket.sendall(command.encode(self.ENCODING))

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

        :return: The contents of the reply packet from BEGIN to END as a str.
        :raises LircSocketTimeoutError: If recv does not find any data after
            self.socket_timeout amount of seconds.
        :raises LircSocketError: If something else went wrong with the socket.
        """
        try:
            BUFFER_LENGTH = 256
            buffer = ""
            data = self.__socket.recv(BUFFER_LENGTH)

            # Ignore recieve requests that the socket caches
            while "BEGIN" not in data.decode(self.ENCODING):
                data = self.__socket.recv(BUFFER_LENGTH)

            buffer += data.decode(self.ENCODING)

            while not buffer.endswith("END\n"):
                data = self.__socket.recv(BUFFER_LENGTH)
                buffer += data.decode(self.ENCODING)

            return buffer
        except (socket.timeout, socket.error) as e:
            err = e.args[0]
            if err == "timed out":
                raise LircSocketTimeoutError(
                    f"could not find any data on the socket after "
                    f"{self.socket_timeout} seconds, socket timed out."
                )
            else:
                raise LircSocketError(e)

    def __parse_reply_packet(self, packet: str) -> LircResponse:
        """
        Parse the reply packet from lircd.

        :param packet: The reply packet from lirc.

        :return: An LircResponse containing the command sent,
            whether it was successful, and any other data, if any was sent.
        """
        lines = packet.split("\n")
        current_index = 0
        response = LircResponse("", False, [])

        if lines[current_index] == "BEGIN":
            current_index += 1
        else:
            return response

        response.command = lines[current_index]
        current_index += 1

        response.success = True if lines[current_index] == "SUCCESS" else False
        current_index += 1

        if lines[current_index] == "END":
            return response
        elif lines[current_index] == "DATA":
            current_index += 1
            data_length = int(lines[current_index])
            current_index += 1
        else:
            raise InvalidReplyPacketFormat(
                f"Unknown format for reply packet: \n{lines}"
            )

        for line in islice(lines, current_index, current_index + data_length):
            response.data.append(line)

        return response

    def send_once(self, key: str, remote: str, repeat_count: int = 1) -> LircResponse:
        """
        Send an LIRC SEND_ONCE command.

        Structure of the command:
          * SEND_ONCE <remote-name> <key-name-from-remote-file> [repeat-count]

        The reason the optional repeat-count parameter isn't used in this implementaiton
        is because we want to be able to store all the responses from each command.

        :param key: The name of the key to send.
        :param remote: The remote to use keys from.
        :param repeat_count: The number of times to press this key.

        :return: a LircResponse or a list of LircResponses if repeat_count > 1.
        :rtype: LircResponse or list
        """
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
        """
        return self.__send_command(f"SEND_START {remote} {key}")

    def send_stop(self, key: str, remote: str) -> LircResponse:
        """
        Send an LIRC SEND_STOP command.

        Structure of the command:
          * SEND_STOP <remote-name> <key-name-from-remote-file>

        :param key: The name of the key to start sending.
        :param remote: The remote to use keys from.
        """
        return self.__send_command(f"SEND_STOP")

    def list_remotes(self) -> LircResponse:
        """List all the remotes in LIRC"""
        return self.__send_command("LIST")

    def list_remote_keys(self, remote: str) -> LircResponse:
        """
        List all the keys for a specific remote.

        :param remote: The remote to list the keys of.

        :return: An LircResponse containing the keys in the
            data section.
        """
        return self.__send_command(f"LIST {remote}")

    def set_inputlog(self, path: str) -> LircResponse:
        """Set the path to log all lircd received data to"""
        return self.__send_command(f"SET_INPUTLOG {path}")

    def stop_inputlog(self) -> LircResponse:
        """
        Stop logging to the inputlog path from set_inputlog.

        When calling SET_INPUTLOG without the path argument,
        it will stop logging and close the logfile.
        """
        return self.__send_command("SET_INPUTLOG")

    def version(self) -> LircResponse:
        """Retrieve the version of LIRC"""
        return self.__send_command("VERSION")
