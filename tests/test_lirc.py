import socket
from unittest import mock

import pytest

from lirc import Lirc, LircResponse
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

    mock_lirc._Lirc__socket.recv.return_value = reply_packet
    response = mock_lirc.send_once(KEY, REMOTE, repeat_count=repeat_count)
    mock_lirc._Lirc__socket.sendall.assert_called_with(
        (COMMAND + "\n").encode(mock_lirc._Lirc__encoding)
    )

    if repeat_count > 1:
        assert type(response) == list
        assert len(response) == repeat_count

        for r in response:
            _ensure_lirc_response(r, COMMAND)
    else:
        _ensure_lirc_response(response, COMMAND)


def _ensure_lirc_response(response: LircResponse, command: str, data: list = []):
    assert type(response) == LircResponse
    assert response.command == command
    assert response.data == data
