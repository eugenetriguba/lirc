from pathlib import Path
from typing import List, Union

from .connection.lircd_connection import LircdConnection
from .exceptions import LircdCommandFailureError
from .reply_packet_parser import ReplyPacketParser


class Client:
    """Communicate with the lircd daemon."""

    def __init__(self, connection: LircdConnection = None) -> None:
        """
        Initialize the client by connecting to the lircd socket.

        Args:
            connection: The connection to lircd. Created with defaults
            depending on the operating system if one is not provided.

        Raises:
            TypeError: If connection is not an instance of LircdConnection.
            LircdConnectionError: If the socket cannot connect to the address.
        """
        if not connection:
            connection = LircdConnection()

        if not isinstance(connection, LircdConnection):
            raise TypeError("`connection` must be an instance of `LircdConnection`")

        # Used for start_repeat and stop_repeat
        self.__last_send_start_remote = None
        self.__last_send_start_key = None

        self.__connection = connection
        self.__connection.connect()

    def __send_command(self, command: str) -> Union[str, List[str]]:
        """
        Send a command to lircd.

        Args:
            command: A command from the lircd socket command interface.

        Returns:
            The data from the lirc response packet.
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

    def close(self) -> None:
        """Close the connection to the socket."""
        self.__connection.close()

    def send_once(self, remote: str, key: str, repeat_count: int = 0) -> None:
        """
        Send an lircd SEND_ONCE command.

        Args:
            key: The name of the key to send.
            remote: The remote to use keys from.
            repeat_count: The number of times to repeat this key.
                If this is set to 1, that means this key will be
                sent twice (repeated once).

        .. versionchanged:: 2.0.0
            The repeat_count parameter has been changed to
            have a default value of 0 instead of 1. This ensures
            send_once only sends 1 IR signal instead of sending 1
            and then repeating it (therefore, 2 signals).

        Raises:
            LircdCommandFailure: If the command fails.
        """
        self.__send_command(f"SEND_ONCE {remote} {key} {repeat_count}")

    def send_start(self, remote: str, key: str) -> None:
        """
        Send an lircd SEND_START command.

        This will repeat the given key until
        send_stop is called.

        Args:
            remote: The remote to use keys from.
            key: The name of the key to start sending.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        self.__last_send_start_remote = remote
        self.__last_send_start_key = key
        self.__send_command(f"SEND_START {remote} {key}")

    def send_stop(self, remote: str = "", key: str = "") -> None:
        """
        Send an lircd SEND_STOP command.

        The remote and key default to the remote and key
        last used with ``send_start`` if they are not specified,
        since the most likely use case is sending a ``send_start``
        and then a ``send_stop``.

        Args:
            remote: The remote to stop.
            key: The key to stop sending.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        if not remote and self.__last_send_start_remote:
            remote = self.__last_send_start_remote

        if not key and self.__last_send_start_key:
            key = self.__last_send_start_key

        self.__send_command(f"SEND_STOP {remote} {key}")

    def list_remotes(self) -> List[str]:
        """
        List all the remotes that lirc has in
        its ``/etc/lirc/lircd.conf.d`` folder.

        Raises:
            LircdCommandFailure: If the command fails.

        Returns:
            The list of all remotes.
        """
        return self.__send_command("LIST")

    def list_remote_keys(self, remote: str) -> List[str]:
        """
        List all the keys for a specific remote.

        Args:
            remote: The remote to list the keys of.

        Raises:
            LircdCommandFailure: If the command fails.

        Returns:
            The list of keys from the remote.
        """
        return self.__send_command(f"LIST {remote}")

    def start_logging(self, path: Union[str, Path]) -> None:
        """
        Send a lircd SET_INPUTLOG command which sets
        the path to log all lircd received data to.

        Args:
            path: The path to start logging lircd recieved data to.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        self.__send_command(f"SET_INPUTLOG {path}")

    def stop_logging(self) -> None:
        """
        Stop logging to the inputlog path from start_logging.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        # When calling SET_INPUTLOG without the path argument,
        # it will stop logging and close the logfile.
        self.__send_command("SET_INPUTLOG")

    def version(self) -> str:
        """
        Retrieve the version of LIRC

        Raises:
            LircdCommandFailure: If the command fails.

        Returns:
            The version of LIRC being used.
        """
        return self.__send_command("VERSION")

    def driver_option(self, key: str, value: str) -> None:
        """
        Set driver-specific option named key to given value.

        Args:
            key: The key to set for the driver.
            value: The value for the key to set.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        self.__send_command(f"DRV_OPTION {key} {value}")

    def simulate(
        self, remote: str, key: str, repeat_count: int = 1, keycode: int = 0
    ) -> None:
        """
        Simulate an IR event.

        The ``--allow-simulate`` command line option to lircd must be active for this
        command not to fail.

        Lircd Format:
            <code> <repeat count> <button name> <remote control name>

            Example:
                0000000000f40bf0 00 KEY_UP ANIMAX

        Args:
            remote: The remote to simulate key presses from.
            key: The key on the remote to simulate.
            repeat_count: The number of times to repeat the simulated key press.
            keycode: lircd(8) describes this option as a 16 hexadecimal digit
                number encoding of the IR signal. However, it says it is depreciated
                and should be ignored.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        self.__send_command(
            "SIMULATE %016d %02d %s %s\n" % (keycode, repeat_count, key, remote)
        )

    def set_transmitters(self, transmitters: Union[int, List[int]]) -> None:
        """
        Set the active transmitters.

        Example:
            import lirc

            client = lirc.Client()

            client.set_transmitters(1)

            client.set_transmitters([1,3,5])

        Args:
            transmitters: The transmitters to set active.

        Raises:
            LircdCommandFailure: If the command fails.
        """
        mask = transmitters

        if isinstance(transmitters, List):
            mask = 0
            for transmitter in transmitters:
                mask |= 1 << (int(transmitter) - 1)

        self.__send_command(f"SET_TRANSMITTERS {mask}")
