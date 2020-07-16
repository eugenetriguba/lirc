import os

import pytest

from lirc import (
    InvalidReplyPacketFormatError,
    Lirc,
    LircResponse,
    LircSocketTimeoutError,
)


# TODO: test this per OS!
def test_default_lirc_init(mock_socket):
    TIMEOUT = 5
    Lirc(socket=mock_socket, timeout=TIMEOUT)
    # mock_socket.connect.assert_called_with(mock_lirc.DEFAULT_SOCKET_PATH)
    mock_socket.settimeout.assert_called_with(TIMEOUT)


def test_lirc_custom_path(mock_socket):
    CUSTOM_PATH = "CUSTOM"
    Lirc(socket=mock_socket, address=CUSTOM_PATH)

    mock_socket.connect.assert_called_with(CUSTOM_PATH)


def test_custom_path_lirc_init(mock_socket):
    TEST_SOCKET_PATH = "test_path"
    Lirc(socket=mock_socket, address=TEST_SOCKET_PATH)
    mock_socket.connect.assert_called_with(TEST_SOCKET_PATH)


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
