from enum import IntEnum, auto
from typing import List

from .exceptions import LircdInvalidReplyPacketError


class ReplyPacketParser:
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
    """

    class State(IntEnum):
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
        SUCCESS = auto()
        FAIL = auto()
        UNDETERMINED = auto()

    def __init__(self):
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
    def data(self) -> List:
        return self.__data_response

    @property
    def is_finished(self) -> bool:
        return self.__state == self.State.FINISHED

    @property
    def success(self) -> bool:
        return self.__command_result == self.Result.SUCCESS

    def __begin(self, line: str) -> None:
        if line == "BEGIN":
            self.__state = self.State.COMMAND
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected a BEGIN line from lircd, got `{line}`."
            )

    def __command(self, line: str) -> None:
        if line == "SIGHUP":
            self.__state = self.State.SIGHUP_END
        elif line:
            self.__state = self.State.RESULT
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected a command line from lircd, got `{line}`."
            )

    def __result(self, line: str) -> None:
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
        if line == "END":
            self.__state = self.State.FINISHED
        elif line == "DATA":
            self.__state = self.State.LINE_COUNT_LEFT
        else:
            raise LircdInvalidReplyPacketError(
                f"Expected an END or DATA line from lircd, got `{line}`."
            )

    def __line_count_left(self, line: str) -> None:
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
        self.__data_response.append(line)
        if len(self.__data_response) >= self.__lines_left:
            self.__state = self.State.END

    def __sighup_end(self, line: str) -> None:
        """
        SIGHUP packages may appear just after a command has been sent
        to lircd, so this is to make sure they are not confused with
        replies. If we encounter it, we reset and read in another packet.
        """
        if line == "END":
            self.__init__()
        else:
            raise LircdInvalidReplyPacketError(
                "Expected an END line with the received SIGHUP packet from "
                f"lircd, got `{line}` instead."
            )

    def __end(self, line: str) -> None:
        if line == "END":
            self.__state = self.State.FINISHED
        else:
            raise LircdInvalidReplyPacketError(
                "Expected an END line from lircd's reply packet, "
                f"got `{line}` instead."
            )

    def feed(self, line: str) -> None:
        line = line.strip()

        if not line:
            return

        self.__fsm[self.__state](line)
