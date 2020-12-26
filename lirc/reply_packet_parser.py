from enum import IntEnum, auto

from .exceptions import LircdInvalidReplyPacketError


class ReplyPacketParser:
    class State(IntEnum):
        """States that this FSM can be in."""

        BEGIN = auto()
        COMMAND = auto()
        RESULT = auto()
        DATA = auto()
        LINE_COUNT_LEFT = auto()
        DATA_BODY = auto()
        SIGHUP_END = auto()
        END = auto()
        FINISHED = auto()

    class Result(IntEnum):
        """
        Packet parsing results. We start at undetermined
        and move to either success or fail.
        """

        SUCCESS = auto()
        FAIL = auto()
        UNDETERMINED = auto()

    def __init__(self):
        """
        Reads and parses reply packets sent from lircd.

        The reply packet is parsed by setting up a fsm
        (finite state machine) and using an internal state
        to keep track of where we are in the process.

        Reply packet format:

            BEGIN
            <command>
            [SUCCESS|ERROR]
            [DATA
            n
            n lines of data]
            END

        SIGHUP Format:

            BEGIN
            SIGHUP
            END

        The only other situation when lircd broadcasts to all
        clients is when it receives the SIGHUP signal and
        successfully re-reads its config file. Then it will
        send a SIGHUP packet to its clients indicating that
        its configuration might have changed. If we receive
        this signal, we'll need to read in another packet.

        Usage:
            parser = ReplyPacketParser()
            conn = LircdConnection()
            while not parser.is_finished():
                parser.feed(conn.readline())

            # Now check parser.data for response data
            # and parser.success for whether or not the command
            # succeeded.
        """
        # Maps states to functions. This allows us to feed()
        # the given line to the function at our current state.
        # That function is then responsible for handling any errors
        # and advancing the state forward.
        self.__fsm = {
            self.State.BEGIN: self.__begin,
            self.State.COMMAND: self.__command,
            self.State.RESULT: self.__result,
            self.State.DATA: self.__data,
            self.State.LINE_COUNT_LEFT: self.__line_count_left,
            self.State.DATA_BODY: self.__data_body,
            self.State.SIGHUP_END: self.__sighup_end,
            self.State.END: self.__end,
        }
        self.__state = self.State.BEGIN
        self.__command_result = self.Result.UNDETERMINED
        self.__data_response = []
        self.__lines_left = None

    @property
    def data(self) -> list:
        """
        Retrieves the data response of the reply packet.

        Returns:
            The data response.
        """
        return self.__data_response

    @property
    def is_finished(self) -> bool:
        """
        Checks whether we are in the finished state.

        Returns:
            True if we are in the finished state; False otherwise.
        """
        return self.__state == self.State.FINISHED

    @property
    def success(self) -> bool:
        """
        Checks whether we have a success result.

        Returns:
            True if the command result is success; False otherwise.
        """
        return self.__command_result == self.Result.SUCCESS

    def __begin(self, line: str) -> None:
        """
        Handles the BEGIN state. This should be the
        state we start in and transition to reading in
        the command.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If line is not BEGIN.
        """
        if line == "BEGIN":
            self.__state = self.State.COMMAND
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected a BEGIN line from lircd, got `{line}`."
            )

    def __command(self, line: str) -> None:
        """
        Handles the COMMAND state. For parsing the reply packet,
        we don't care too much about this state. As long as we got
        a command, we move on to check the result. However, the
        command could be a SIGHUP in which case, we want to ensure
        it is properly handled.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If the line is empty.
                However, this error is likely unreachable since
                if the line is empty, feed() simply returns.
        """
        if line == "SIGHUP":
            self.__state = self.State.SIGHUP_END
        elif line:
            self.__state = self.State.RESULT
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected a command line from lircd, got `{line}`."
            )

    def __result(self, line: str) -> None:
        """
        Handles the RESULT state. An lircd result is
        either SUCCESS or ERROR, followed by data.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If the line is not SUCCESS or ERROR.
        """
        if line in ["SUCCESS", "ERROR"]:
            self.__state = self.State.DATA
            self.__command_result = (
                self.Result.SUCCESS if line == "SUCCESS" else self.Result.FAIL
            )
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected a result line from lircd, got `{line}`."
            )

    def __data(self, line: str) -> None:
        """
        Handles the DATA state. In this state,
        we could either be finished now if there is
        no data from the response or move to reading
        in how many lines of data there is.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If line is not END or DATA.
        """
        if line == "END":
            self.__state = self.State.FINISHED
        elif line == "DATA":
            self.__state = self.State.LINE_COUNT_LEFT
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected an END or DATA line from lircd, got `{line}`."
            )

    def __line_count_left(self, line: str) -> None:
        """
        Handles the LINE COUNT LEFT state. This corresponds
        to the `n` line in the packet format, since it tells
        us how many lines of data we have to read in.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If line cannot be coerced
            into an integer, since we expect it to be the remaining
            lines left at this state.
        """
        try:
            self.__lines_left = int(line)
        except ValueError:
            raise LircdInvalidReplyPacketError(
                f"Expected a remaining line count line from lircd, got `{line}`."
            )

        self.__state = (
            self.State.END if self.__lines_left == 0 else self.State.DATA_BODY
        )

    def __data_body(self, line: str) -> None:
        """
        Handles the DATA BODY state by appending
        every line we recieve to the data response.

        Because the reply packet tells us how many lines
        of data we have, we can easily reference this to
        know when we are done and should move on to the
        END state.

        Args:
            line: A line read in from an lircd connection.
        """
        self.__data_response.append(line)
        if len(self.__data_response) >= self.__lines_left:
            self.__state = self.State.END

    def __sighup_end(self, line: str) -> None:
        """
        Handle a SIGHUP END line by resetting the parser.

        SIGHUP packages may appear just after a command has been sent
        to lircd, so this is to make sure they are not confused with
        replies. If we encounter it, we reset and read in another packet.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If the line does not contain END.
        """
        if line == "END":
            self.__init__()
        else:
            raise LircdInvalidReplyPacketError(
                "Expected an END line with the received SIGHUP packet from "
                f"lircd, got `{line}` instead."
            )

    def __end(self, line: str) -> None:
        """
        Handle a END line by transitioning the parser's state
        to finished. This means we have finished reading in the
        reply packet.

        Args:
            line: A line read in from an lircd connection.

        Raises:
            LircdInvalidReplyPacketError: If the line does not contain END.
        """
        if line == "END":
            self.__state = self.State.FINISHED
        else:
            raise LircdInvalidReplyPacketError(
                "Expected an END line from lircd's reply packet, "
                f"got `{line}` instead."
            )

    def feed(self, line: str) -> None:
        """
        Feed a line from the reply packet into the parser.

        Args:
            A line from the lircd connection to feed in.
        """
        line = line.strip()

        if not line:
            return

        self.__fsm[self.__state](line)
