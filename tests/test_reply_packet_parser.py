import os

import pytest

from lirc import InvalidReplyPacketFormatError, LircSocketTimeoutError


@pytest.mark.parametrize(
    "reply_packet", [b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n"]
)
def test_read_reply_packet(mock_lirc_and_socket, reply_packet):
    mock_lirc, mock_socket = mock_lirc_and_socket
    mock_socket.recv.return_value = reply_packet

    retrieved_packet = mock_lirc._Lirc__read_reply_packet()

    mock_socket.recv.assert_called_with(256)
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
