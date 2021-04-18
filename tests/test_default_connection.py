import socket
from unittest.mock import patch

import pytest

from lirc.connection.default_connection import DefaultConnection
from lirc.exceptions import UnsupportedOperatingSystemError


@pytest.mark.parametrize(
    "os, expected_socket, expected_address",
    [
        (
            "Windows",
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            ("localhost", 8765),
        ),
        (
            "Linux",
            socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
            "/var/run/lirc/lircd",
        ),
        (
            "Darwin",
            socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
            "/opt/local/var/run/lirc/lircd",
        ),
    ],
)
@patch("platform.system")
def test_default_connection_has_correct_os_specific_socket_and_address(
    patched_system, os, expected_socket, expected_address
):
    """
    lirc.connection.default_connection.DefaultConnection

    Ensure that the DefaultConnection retrieves the correct socket
    and address for each support operating system.
    """
    patched_system.return_value = os

    default_conn = DefaultConnection()  # SUT

    assert default_conn.socket.family == expected_socket.family
    assert default_conn.socket.type == expected_socket.type
    assert default_conn.address == expected_address


@pytest.mark.parametrize("prop", ["socket", "address"])
@patch("platform.system")
def test_default_connection_raises_error_on_unsupported_os(patched_system, prop):
    """
    lirc.connection.default_connection.DefaultConnection.socket
    lirc.connection.default_connection.DefaultConnection.address

    Ensure that trying to retrieve the socket or address on an unsupported
    OS raises an UnsupportedOperatingSystemError.
    """
    patched_system.return_value = "FreeBSD"

    with pytest.raises(UnsupportedOperatingSystemError) as error:
        default_conn = DefaultConnection()
        getattr(default_conn, prop)  # SUT

    assert "FreeBSD is not supported" in str(error)
