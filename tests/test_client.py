import pytest

from lirc import Client, LircdConnection
from lirc.exceptions import LircdCommandFailureError


def test_that_custom_connections_can_be_used(mock_socket):
    """
    lirc.Client.__init__

    Ensure we can pass in custom connections using the
    keyword argument instead of relying on the default.
    """
    connection = LircdConnection(socket=mock_socket)

    client = Client(connection=connection)  # SUT

    assert client._Client__connection == connection


def test_that_custom_connection_that_is_not_a_lircd_connection_raises_error():
    """
    lirc.Client.__init__

    Ensure that passing in something that is not an instance of
    LircdConnection raise a TypeError.
    """
    with pytest.raises(TypeError) as error:
        Client(connection=Client())  # SUT

    assert "must be an instance of `LircdConnection`" in str(error)


def test_that_close_closes_the_socket(mock_client_and_connection):
    """
    lirc.Client.close

    Ensure that a call to close() calls the socket's close().
    """
    client, connection = mock_client_and_connection

    client.close()  # SUT

    connection._LircdConnection__socket.close.assert_called()


@pytest.mark.parametrize(
    "client_command, args, lircd_command",
    [
        ("send", {"remote": "REMOTE", "key": "KEY"}, "SEND_ONCE REMOTE KEY 1"),
        (
            "send",
            {"remote": "REMOTE", "key": "KEY", "repeat_count": 5},
            "SEND_ONCE REMOTE KEY 5",
        ),
        ("start_repeat", {"remote": "REMOTE", "key": "KEY"}, "SEND_START REMOTE KEY"),
        ("stop_repeat", {}, "SEND_STOP  "),
        ("stop_repeat", {"remote": "REMOTE", "key": "KEY"}, "SEND_STOP REMOTE KEY"),
        ("list_remotes", {}, "LIST"),
        ("list_remote_keys", {"remote": "REMOTE"}, "LIST REMOTE"),
        ("start_logging", {"path": "PATH"}, "SET_INPUTLOG PATH"),
        ("stop_logging", {}, "SET_INPUTLOG"),
        ("version", {}, "VERSION"),
        ("driver_option", {"key": "KEY", "value": "VALUE"}, "DRV_OPTION KEY VALUE"),
        (
            "simulate",
            {"remote": "REMOTE", "key": "KEY"},
            "SIMULATE 0000000000000000 01 KEY REMOTE",
        ),
        (
            "simulate",
            {"remote": "REMOTE", "key": "KEY", "repeat_count": 4, "keycode": 53},
            "SIMULATE 0000000000000053 04 KEY REMOTE",
        ),
        ("set_transmitters", {"transmitters": 5}, "SET_TRANSMITTERS 5"),
        ("set_transmitters", {"transmitters": [10, 1, 1]}, "SET_TRANSMITTERS 513"),
    ],
)
def test_that_client_commands_send_the_correct_command(
    mock_client_and_connection, client_command, args, lircd_command
):
    """
    lirc.Client.send
    lirc.Client.start_repeat
    lirc.Client.stop_repeat
    lirc.Client.list_remotes
    lirc.Client.list_remote_keys
    lirc.Client.start_logging
    lirc.Client.stop_logging
    lirc.Client.version
    lirc.Client.driver_option
    lirc.Client.simulate
    lirc.Client.set_transmitters

    Ensure that all the commands that are wrappers around the lircd
    commands send the correct lircd command when given various arguments.

    Args:
        mock_client_and_connection: Mocked client and connection to lircd.
        client_command: The commond on the Client to call.
        args: The args to call the client command with.
        lircd_command: The expected corresponding command sent to lircd.
    """
    client, connection = mock_client_and_connection
    connection._LircdConnection__socket.recv.return_value = (
        b"BEGIN\nCOMMAND\nSUCCESS\nEND\n"
    )

    getattr(client, client_command)(**args)  # SUT

    connection._LircdConnection__socket.sendall.assert_called_with(
        (lircd_command + "\n").encode("utf-8")
    )


def test_unsuccessful_command_raises_custom_exception(mock_client_and_connection):
    """
    lirc.client.__send_command (which all lircd wrapper functions use)

    Ensure that a lircd reply packet which is not successful raises a
    LircdCommandFailureError.
    """
    client, connection = mock_client_and_connection
    connection._LircdConnection__socket.recv.return_value = (
        b"BEGIN\nCOMMAND\nERROR\nEND\n"
    )

    with pytest.raises(LircdCommandFailureError) as error:
        client.send('remote', 'key')

    assert 'The `SEND_ONCE remote key 1` command sent to lircd failed: []' in str(error)


def test_last_start_repeat_remote_and_key_is_used(mock_client_and_connection):
    """
    lirc.client.start_repeat
    lirc.client.stop_repeat

    Ensure that when we call start_repeat, a subsequent call
    to stop_repeat will use the remote and key start_repeat
    had passed in as args if no args are provided to stop_repeat.
    """
    client, connection = mock_client_and_connection
    connection._LircdConnection__socket.recv.return_value = (
        b"BEGIN\nCOMMAND\nSUCCESS\nEND\n"
    )
    client.start_repeat('remote', 'key')

    client.stop_repeat()  # SUT

    connection._LircdConnection__socket.sendall.assert_called_with(
        "SEND_STOP remote key\n".encode("utf-8")
    )
