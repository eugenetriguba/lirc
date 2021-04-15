import pytest

from lirc.exceptions import LircdInvalidReplyPacketError
from lirc.reply_packet_parser import ReplyPacketParser


def test_starting_state_of_reply_packet_parser():
    """
    lirc.reply_packet_parser.ReplyPacketParser.__init__

    Ensure the initial state of the ReplyPacketParser
    is what is expected.
    """
    parser = ReplyPacketParser()  # SUT

    assert not parser.is_finished
    assert not parser.success
    assert parser.data == []


def test_parsing_version_reply_packet():
    """
    lirc.reply_packet_parser.ReplyPacketParser.feed

    Ensure that a reply packet from a `VERSION` command
    is parsed correctly.
    """
    parser = ReplyPacketParser()
    packet = ["BEGIN\n", "VERSION\n", "SUCCESS\n", "DATA\n", "1\n", "0.10.1\n", "END\n"]

    for line in packet:
        parser.feed(line)  # SUT

    assert parser.success
    assert parser.is_finished
    assert parser.data == ["0.10.1"]


def test_parsing_remotes_reply_packet():
    """
    lirc.reply_packet_parser.ReplyPacketParser.feed

    Ensure that a reply packet from a `LIST` command
    is parsed correctly.
    """
    parser = ReplyPacketParser()
    packet = [
        "BEGIN\n",
        "LIST\n",
        "SUCCESS\n",
        "DATA\n",
        "2\n",
        "some-remote\n",
        "some-other-remote\n",
        "END\n",
    ]

    for line in packet:
        parser.feed(line)  # SUT

    assert parser.success
    assert parser.is_finished
    assert parser.data == ["some-remote", "some-other-remote"]


def test_handling_of_sighup_packet():
    """
    lirc.reply_packet_parser.ReplyPacketParser.feed

    Ensure that a reply packet from a `SIGHUP` command
    is parsed correctly and resets the reply parser since
    this just indicates we've parsed
    """
    parser = ReplyPacketParser()
    packet = [
        "BEGIN\n",
        "SIGHUP\n",
        "END\n",
    ]

    for line in packet:
        parser.feed(line)  # SUT

    # The parser should be reset if we recieved a SIGHUP
    # so success would be false and is would not be finished.
    assert not parser.success
    assert not parser.is_finished
    assert parser.data == []


def test_error_with_send_once():
    """
    lirc.reply_packet_parser.ReplyPacketParser.feed

    Ensure that an ERROR with a SEND_ONCE command is
    parsed correctly.
    """
    parser = ReplyPacketParser()
    packet = [
        "BEGIN\n",
        "SEND_ONCE remote key_power 1\n",
        "ERROR",
        "DATA",
        "1",
        "hardware does not support sending",
        "END",
    ]

    for line in packet:
        parser.feed(line)  # SUT

    assert not parser.success
    assert parser.is_finished
    assert parser.data == ["hardware does not support sending"]


def test_no_line_passed_to_feed():
    """
    lirc.reply_packet_parser.ReplyPacketParser.feed

    Ensure that an empty line or no line (such as None)
    does nothing to advance the parser.
    """
    parser = ReplyPacketParser()

    parser.feed("")  # SUT

    assert not parser.success
    assert not parser.is_finished
    assert parser.data == []


@pytest.mark.parametrize(
    "packet",
    [
        [
            "BEGIN\n",
            "SIGHUP\n",
            "invalid-expected-end\n",
        ],
        [
            "BEGIN\n",
            "VERSION\n",
            "SUCCESS\n",
            "DATA\n",
            "1\n",
            "0.10.1\n",
            "invalid-expected-end\n",
        ],
        ["NOTBEGIN"],
        [
            "BEGIN\n",
            "VERSION\n",
            "not-SUCCESS-or-ERROR\n",
            "DATA\n",
            "1\n",
            "0.10.1\n",
            "END\n",
        ],
        [
            "BEGIN\n",
            "VERSION\n",
            "SUCCESS\n",
            "not-DATA-or-END\n",
            "1\n",
            "0.10.1\n",
            "END\n",
        ],
        [
            "BEGIN\n",
            "VERSION\n",
            "SUCCESS\n",
            "DATA\n",
            "not-a-line-count-left-number\n",
            "0.10.1\n",
            "END\n",
        ],
    ],
)
def test_invalid_end_line_raises_error(packet):
    """
    lirc.reply_packet_parser.ReplyPacketParser.feed

    Ensure that invalid reply packets raise an error.
    """
    parser = ReplyPacketParser()

    with pytest.raises(LircdInvalidReplyPacketError):
        for line in packet:
            parser.feed(line)  # SUT


@pytest.mark.parametrize("line", [None, "", False])
def test_command_state_raises_exception_on_empty_line(line):
    """
    lirc.reply_packet_parser.ReplyPacketParser.__command

    Ensure that the command state raises an error when
    an empty (or falsey) line is passed. This scenario
    is unlikely to happen in practical use since the .feed()
    method simply returns if we recieved an empty line.
    """
    parser = ReplyPacketParser()

    with pytest.raises(LircdInvalidReplyPacketError):
        parser._ReplyPacketParser__command(line)
