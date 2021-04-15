import socket
from collections import deque
from unittest.mock import patch

import pytest

from lirc import LircdConnection
from lirc.exceptions import LircdConnectionError, LircdSocketError


def test_close_closes_the_socket_connection(mock_connection):
    """
    lirc.connection.lircd_connection.LircdConnection.close

    Ensure that a call to close calls the socket's close method.
    """
    mock_connection.close()  # SUT

    mock_connection._LircdConnection__socket.close.assert_called()


def test_that_retrieving_the_address_property_retrieves_the_address(mock_socket):
    """
    lirc.connection.lircd_connection.LircdConnection.address

    Ensure that that trying to retrieve the address property
    retrieves the expected address.
    """
    expected_address = "/var/does/not/exist"
    conn = LircdConnection(socket=mock_socket, address=expected_address)

    address = conn.address  # SUT

    assert address == expected_address


def test_that_attribute_error_is_raised_on_invalid_socket():
    """
    lirc.connection.lircd_connection.LircdConnection.__init__

    Ensure that an error is raised when an invalid socket is passed
    to the LircdConnection constructor.
    """
    with pytest.raises(AttributeError):
        LircdConnection(socket=5)  # SUT


def test_that_connection_error_is_raised_on_invalid_address():
    """
    lirc.connection.lircd_connection.LircdConnection.connect

    Ensure that an invalid address raises an LircdConnectionError
    when we try to connect.
    """
    with pytest.raises(LircdConnectionError):
        LircdConnection(address="invalid thing").connect()  # SUT


def test_that_a_socket_with_an_invalid_address_raises_error(mock_socket):
    """
    lirc.connection.lircd_connection.LircdConnection.connect

    Ensure that a LircdConnectionError is raised if cannot connect
    to lircd at the given address (if the socket raises a FileNotFoundError).
    """
    mock_socket.connect.side_effect = FileNotFoundError

    with pytest.raises(LircdConnectionError) as error:
        LircdConnection(socket=mock_socket).connect()  # SUT

    assert "Could not connect to lircd" in str(error)


def test_that_a_socket_raises_general_error(mock_socket):
    """
    lirc.connection.lircd_connection.LircdConnection.connect

    Ensure that a LircdConnectionError is raised if any general
    exception is raised by the connection to the socket, such as
    an InterruptedError if a signal occurs.
    """
    mock_socket.connect.side_effect = InterruptedError("interrupted by a signal")

    with pytest.raises(LircdConnectionError) as error:
        LircdConnection(socket=mock_socket).connect()  # SUT

    assert "interrupted by a signal" in str(error)


@pytest.mark.parametrize("test_command", ["SEND_ONCE REMOTE KEY", ""])
def test_that_send_adds_a_newline_to_the_end(mock_connection, test_command):
    """
    lirc.connection.lircd_connection.LircdConnection.send

    Ensure a newline is added to the command we pass to send()
    if one is not present.
    """
    mock_connection.send(test_command)  # SUT

    mock_connection._LircdConnection__socket.sendall.assert_called_with(
        f"{test_command}\n".encode("utf-8")
    )


def test_that_send_does_not_add_too_many_newlines(mock_connection):
    """
    lirc.connection.lircd_connection.LircdConnection.send

    Ensure a newline is not added to the end of the command if
    one is already present.
    """
    command = "SEND_ONCE REMOTE KEY\n"

    mock_connection.send(command)  # SUT

    mock_connection._LircdConnection__socket.sendall.assert_called_with(
        f"{command}".encode("utf-8")
    )


@pytest.mark.parametrize("test_command", [5, False, 0.1, b"hello"])
def test_that_send_raises_a_type_error_for_parameters_that_are_not_strings(
    mock_connection, test_command
):
    """
    lirc.connection.lircd_connection.LircdConnection.send

    Ensure that a TypeError is raised if the parameter we passed is not
    a string. This is to prevent errors such as when we try to add an
    ending newline or check if the passed in arg has a newline.
    """
    with pytest.raises(TypeError) as error:
        mock_connection.send(test_command)  # SUT

    assert "data parameter to send() must be a string" in str(error)


@pytest.mark.parametrize(
    "buffer_payload, expected_item",
    [("BEGIN\nSIGHUP\nEND\n".split("\n"), "BEGIN"), ([""], "")],
)
def test_that_readline_uses_buffer_if_items_are_present_in_it(
    mock_connection, buffer_payload, expected_item
):
    """
    lirc.connection.lircd_connection.LircdConnection.readline

    Ensure that readline uses the buffer if there are items in it.
    """
    mock_connection._LircdConnection__buffer.extend(buffer_payload)

    line = mock_connection.readline()  # SUT

    assert line == expected_item


@pytest.mark.parametrize(
    "socket_payload, expected_return, expected_buffer",
    [
        (b"BEGIN\nTEST\nEND\n", "BEGIN", deque(["TEST", "END"])),
        (b"BEGIN\nTEST\nEND", "BEGIN", deque(["TEST", "END"])),
        (b"", "", deque()),
    ],
)
def test_that_readline_retrieves_data_from_socket_and_adds_to_buffer(
    mock_connection, socket_payload, expected_return, expected_buffer
):
    """
    lirc.connection.lircd_connection.LircdConnection.readline

    Ensure that when we call readline(), it adds to the buffer if we
    retrieved more than a single line.
    """
    mock_connection._LircdConnection__socket.recv.return_value = socket_payload

    line = mock_connection.readline()  # SUT

    assert line == expected_return
    assert mock_connection._LircdConnection__buffer == expected_buffer


@patch("socket.socket.recv")
def test_that_readline_raises_timeout_error(patched_recv):
    """
    lirc.connection.lircd_connection.LircdConnection.readline

    Ensure that a TimeoutError is raised from readline() if the
    socket times out (raises socket.timeout).
    """
    patched_recv.side_effect = socket.timeout
    connection = LircdConnection()

    with pytest.raises(TimeoutError) as error:
        connection.readline()  # SUT

    assert "could not find any data on the socket" in str(error)


@patch("socket.socket.recv")
def test_that_readline_raises_lircd_socket_error(patched_recv):
    """
    lirc.connection.lircd_connection.LircdConnection.readline

    Ensure that a general LircdSocketError is raised from readline()
    if the socket raises `socket.error`.
    """
    patched_recv.side_effect = socket.error
    connection = LircdConnection()

    with pytest.raises(LircdSocketError) as error:
        connection.readline()  # SUT

    assert "An error occurred while reading from the lircd socket" in str(error)
