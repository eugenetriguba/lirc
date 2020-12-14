import time
from collections import deque
from platform import system
from unittest import mock

import pytest

from lirc import LircdConnection
from lirc.exceptions import LircdConnectionError


@mock.patch("socket.socket")
@mock.patch("platform.system")
@pytest.mark.parametrize("os_name", ["Windows", "Darwin", "Linux"])
def test_socket_and_address_have_correct_cross_platform_values(
    mocked_system, mocked_socket, os_name
):
    if system() != os_name:
        return

    mocked_system.return_value = os_name

    connection = LircdConnection()

    expected_socket = connection._LircdConnection__socket
    expected_address = connection._LircdConnection__address

    assert connection.socket.family == expected_socket.family
    assert connection.socket.type == expected_socket.type
    assert connection.address == expected_address


def test_close_closes_the_socket_connection(mock_connection):
    mock_connection.close()
    mock_connection.socket.close.assert_called()


def test_that_connection_error_is_raised_on_invalid_address():
    with pytest.raises(LircdConnectionError):
        LircdConnection(address="invalid thing").connect()


def test_that_attribute_error_is_raised_on_invalid_socket():
    with pytest.raises(AttributeError):
        LircdConnection(socket=5).connect()


@pytest.mark.parametrize("test_command", ["SEND_ONCE REMOTE KEY", ""])
def test_that_send_adds_a_newline_to_the_end_if_not_present(
    mock_connection, test_command
):
    mock_connection.send(test_command)
    mock_connection.socket.sendall.assert_called_with(
        f"{test_command}\n".encode("utf-8")
    )


@pytest.mark.parametrize("test_command", [5, False, 0.1, b"hello"])
def test_that_send_raises_a_type_error_for_parameters_that_are_not_strings(
    mock_connection, test_command
):
    with pytest.raises(TypeError) as error:
        mock_connection.send(test_command)

    assert "data parameter to send() must be a string" in str(error)


@pytest.mark.parametrize("test_command", ["SEND_ONCE REMOTE KEY\n"])
def test_that_send_sends_the_command_unaltered_to_the_socket_if_in_correct_format(
    mock_connection, test_command
):
    mock_connection.send(test_command)
    mock_connection.socket.sendall.assert_called_with(test_command.encode("utf-8"))


@pytest.mark.parametrize(
    "buffer_payload, expected_item",
    [("BEGIN\nSIGHUP\nEND\n".split("\n"), "BEGIN"), ([""], "")],
)
def test_that_readline_uses_buffer_if_items_are_present_in_it(
    mock_connection, buffer_payload, expected_item
):
    mock_connection._LircdConnection__buffer.extend(buffer_payload)
    assert mock_connection.readline() == expected_item


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
    mock_connection.socket.recv.return_value = socket_payload

    line = mock_connection.readline()

    assert line == expected_return
    assert mock_connection._LircdConnection__buffer == expected_buffer


def test_that_readline_raises_timeout_error_if_no_data_from_socket():
    timeout = 0.001
    error_threshold = 0.01
    connection = LircdConnection(timeout=timeout)

    start_time = time.time()
    with pytest.raises(TimeoutError) as error:
        connection.readline()
    end_time = time.time()
    delta = abs(start_time - end_time)

    assert delta < timeout + error_threshold
    assert f"could not find any data on the socket after {timeout}" in str(error)
