import pytest

from lirc import Client, LircdConnection


def test_that_custom_connections_can_be_used(mock_socket):
    connection = LircdConnection(socket=mock_socket)
    client = Client(connection=connection)

    assert client._Client__connection == connection


def test_that_custom_connection_that_is_not_a_lircd_connection_raises_error():
    with pytest.raises(ValueError) as error:
        Client(connection=Client())

    assert "must be an instance of `LircdConnection`" in str(error)


def test_that_close_closes_the_socket(mock_client_and_connection):
    client, connection = mock_client_and_connection

    client.close()

    connection.socket.close.assert_called()


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
    client, connection = mock_client_and_connection
    connection.socket.recv.return_value = b"BEGIN\nCOMMAND\nSUCCESS\nEND\n"

    getattr(client, client_command)(**args)

    connection.socket.sendall.assert_called_with((lircd_command + "\n").encode("utf-8"))
