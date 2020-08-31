from typing import List, Union

from .connection.lircd_connection import LircdConnection
from .exceptions import LircdCommandFailureError
from .reply_packet_parser import ReplyPacketParser


class Client:
    """Communicate with the lircd daemon."""

    def __init__(self, connection: LircdConnection = LircdConnection()) -> None:
        """
        Initialize the client by connecting to the lircd socket.

        Args:
            connection: The connection to lircd. Created with defaults
            depending on the operating system if one is not provided.

        Raises:
            ValueError: If connection is not a LircdConnection.
            LircdConnectionError: If the socket cannot connect to the address.
        """
        # Used for start_repeat and stop_repeat
        self.__last_send_start_remote = None
        self.__last_send_start_key = None

        if not isinstance(connection, LircdConnection):
            raise ValueError("`connection` must be an instance of `LircdConnection`")

        self.__connection = connection
        self.__connection.connect()

    def __send_command(self, command: str) -> Union[str, List[str]]:
        """
        Send a command to lircd.

        Args:
            command: A command from the lircd socket command interface.

        Returns:
            A response object containing information on the command sent.
        """
        self.__connection.send(command)

        parser = ReplyPacketParser()
        while not parser.is_finished:
            line = self.__connection.readline()
            parser.feed(line)

        parser_data = parser.data[0] if len(parser.data) == 1 else parser.data

        if not parser.success:
            raise LircdCommandFailureError(
                f"The `{command}` command sent to lircd failed: {parser_data}"
            )

        return parser_data

    def close(self):
        self.__connection.close()

    def send(self, remote: str, key: str, repeat_count: int = 1) -> None:
        """
        Send an lircd SEND_ONCE command.

        Args:
            key: The name of the key to send.
            remote: The remote to use keys from.
            repeat_count: The number of times to press this key.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        self.__send_command(f"SEND_ONCE {remote} {key} {repeat_count}")

    def start_repeat(self, remote: str, key: str) -> None:
        """
        Send an lircd SEND_START command.

        This will repeat the given key until
        stop_repeat is called.

        Args:
            remote: The remote to use keys from.
            key: The name of the key to start sending.

        Returns:
            The response of the command.
        """
        self.__last_send_start_remote = remote
        self.__last_send_start_key = key
        self.__send_command(f"SEND_START {remote} {key}")

    def stop_repeat(self, remote: str = None, key: str = None) -> None:
        """
        Send an lircd SEND_STOP command.

        Args:
            remote: The remote to stop.
            key: The key to stop sending.

            These default to the remote and key
            last used with send_start if not specified,
            since the most likely use case is sending a
            send_start and then a send_stop.

        Returns:
            The response of the command.
        """
        if remote:
            remote_to_stop = remote
        elif self.__last_send_start_remote:
            remote_to_stop = self.__last_send_start_remote
        else:
            remote_to_stop = ""

        if key:
            key_to_stop = key
        elif self.__last_send_start_key:
            key_to_stop = self.__last_send_start_key
        else:
            key_to_stop = ""

        self.__send_command(f"SEND_STOP {remote_to_stop} {key_to_stop}")

    def list_remotes(self) -> List[str]:
        """
        List all the remotes that lirc has in
        its `lircd.conf.d` folder.

        Returns:
            The response of the command.
        """
        return self.__send_command("LIST")

    def list_remote_keys(self, remote: str) -> List[str]:
        """
        List all the keys for a specific remote.

        Args:
            remote: The remote to list the keys of.

        Returns:
            The response of the command.
        """
        return self.__send_command(f"LIST {remote}")

    def start_logging(self, path: str) -> None:
        """
        Send a lircd SET_INPUTLOG command which sets
        the path to log all lircd received data to.

        Returns:
            The response of the command.
        """
        self.__send_command(f"SET_INPUTLOG {path}")

    def stop_logging(self) -> None:
        """
        Stop logging to the inputlog path from start_logging.

        Returns:
            The response of the command.
        """
        # When calling SET_INPUTLOG without the path argument,
        # it will stop logging and close the logfile.
        self.__send_command("SET_INPUTLOG")

    def version(self) -> str:
        """
        Retrieve the version of LIRC

        Returns:
            The response of the command with
            the version in the data field.
        """
        return self.__send_command("VERSION")

    def driver_option(self, key: str, value: str) -> None:
        """
        Set driver-specific option named key to given value.
        """
        self.__send_command(f"DRV_OPTION {key} {value}")

    def simulate(
        self, remote: str, key: str, repeat_count: int = 1, keycode: int = 0
    ) -> None:
        """
        The --allow-simulate command line option must be active for this
        command not to fail.
        """
        self.__send_command(
            "SIMULATE %016d %02d %s %s\n" % (keycode, repeat_count, key, remote)
        )

    def set_transmitters(self, transmitters: Union[int, List[int]]) -> None:
        mask = transmitters

        if isinstance(transmitters, List):
            mask = 0
            for transmitter in transmitters:
                mask |= 1 << (int(transmitter) - 1)

        self.__send_command(f"SET_TRANSMITTERS {mask}")
