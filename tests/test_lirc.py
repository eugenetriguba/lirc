import os
import socket
from unittest import mock

import pytest

from lirc import (
    InvalidReplyPacketFormatError,
    Lirc,
    LircResponse,
    LircSocketTimeoutError,
)
from lirc.lirc import (
    DEFAULT_ADDRESS_DARWIN,
    DEFAULT_ADDRESS_LINUX,
    DEFAULT_ADDRESS_WINDOWS,
)


@mock.patch("socket.socket")
@mock.patch("platform.system")
@pytest.mark.parametrize(
    "os_name, expected_address, expected_socket_parameters",
    [
        ("Windows", DEFAULT_ADDRESS_WINDOWS, (socket.AF_INET, socket.SOCK_STREAM)),
        ("Darwin", DEFAULT_ADDRESS_DARWIN, (socket.AF_UNIX, socket.SOCK_STREAM)),
        ("Linux", DEFAULT_ADDRESS_LINUX, (socket.AF_UNIX, socket.SOCK_STREAM)),
    ],
)
def test_default_lirc_initialization(
    mocked_system, mocked_socket, os_name, expected_address, expected_socket_parameters
):
    mocked_system.return_value = os_name

    lirc = Lirc()
    lirc_socket = lirc._Lirc__socket

    mocked_socket.assert_called_once_with(*expected_socket_parameters)
    lirc_socket.connect.assert_called_with(expected_address)
    lirc_socket.settimeout.assert_called_with(5.0)


def test_custom_lirc_initialization(mock_socket):
    CUSTOM_ADDRESS = "CUSTOM"
    CUSTOM_TIMEOUT = 10.0

    Lirc(socket=mock_socket, address=CUSTOM_ADDRESS, timeout=CUSTOM_TIMEOUT)

    mock_socket.connect.assert_called_with(CUSTOM_ADDRESS)
    mock_socket.settimeout.assert_called_with(CUSTOM_TIMEOUT)


@pytest.mark.parametrize(
    "reply_packet", [b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n"]
)
def test_read_reply_packet(mock_lirc, reply_packet):
    mock_lirc._Lirc__socket.recv.return_value = reply_packet
    retrieved_packet = mock_lirc._Lirc__read_reply_packet()
    mock_lirc._Lirc__socket.recv.assert_called_with(256)
    assert reply_packet == retrieved_packet.encode(mock_lirc._Lirc__encoding)


@pytest.mark.skipif(
    os.environ.get("LIRC_RUN_LONG_TESTS") is None, reason="Test takes too long"
)
@pytest.mark.parametrize("reply_packet", [b"INVALID PACKET"])
def test_read_reply_packet_socket_timeout(mock_lirc, reply_packet):
    with pytest.raises(LircSocketTimeoutError):
        mock_lirc._Lirc__socket.recv.return_value = reply_packet
        mock_lirc._Lirc__read_reply_packet()


@pytest.mark.parametrize(
    "reply_packet, command, success, data, exception",
    [
        (
            "BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n",
            "SEND_ONCE remote key",
            True,
            [],
            None,
        ),
        ("INVALID PACKET", "", False, [], None),
        (
            "BEGIN\nSEND_ONCE remote key\nERROR\nINVALID\n",
            "SEND_ONCE remote key",
            False,
            [],
            InvalidReplyPacketFormatError,
        ),
        (
            "BEGIN\nSEND_ONCE remote key\nERROR\nDATA\n1\nunknown remote: remote\n",
            "SEND_ONCE remote key",
            False,
            ["unknown remote: remote"],
            None,
        ),
        (
            "BEGIN\nSEND_ONCE remote key\nSUCCESS\nDATA\n3\nraa\nblah\nbhal\n",
            "SEND_ONCE remote key",
            True,
            ["raa", "blah", "bhal"],
            None,
        ),
    ],
)
def test_parse_reply_packet(mock_lirc, reply_packet, command, success, data, exception):
    if exception:
        with pytest.raises(exception):
            mock_lirc._Lirc__parse_reply_packet(reply_packet)
    else:
        response = mock_lirc._Lirc__parse_reply_packet(reply_packet)
        assert response.success == success
        assert response.command == command
        assert response.data == data


@pytest.mark.parametrize(
    "reply_packet, repeat_count",
    [
        (b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n", 1),
        (b"BEGIN\nSEND_ONCE remote key\nERROR\nEND\n", 1),
        (b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n", 5),
    ],
)
def test_send_once(mock_lirc, reply_packet, repeat_count):
    REMOTE = "remote"
    KEY = "key"
    COMMAND = f"SEND_ONCE {REMOTE} {KEY}"
    SUCCESS = (
        True if "SUCCESS" in reply_packet.decode(mock_lirc._Lirc__encoding) else False
    )

    mock_lirc._Lirc__socket.recv.return_value = reply_packet
    response = mock_lirc.send_once(KEY, REMOTE, repeat_count=repeat_count)
    mock_lirc._Lirc__socket.sendall.assert_called_with(
        (COMMAND + "\n").encode(mock_lirc._Lirc__encoding)
    )

    if repeat_count > 1:
        assert type(response) == list
        assert len(response) == repeat_count

        for r in response:
            _ensure_lirc_response(r, COMMAND, SUCCESS)
    else:
        _ensure_lirc_response(response, COMMAND, SUCCESS)


def _ensure_lirc_response(
    response: LircResponse, command: str, success: bool, data: list = []
):
    assert type(response) == LircResponse
    assert response.command == command
    assert response.success == success
    assert response.data == data
