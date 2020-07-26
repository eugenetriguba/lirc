# import pytest
#
# from lirc import (
#     LircdCommandFailureError,
#     LircdInvalidReplyPacketError,
#     LircdSocketTimeoutError,
# )
# from lirc.reply_packet_parser import ReplyPacketParser
# from lirc.utils import ENCODING
#
#
# @pytest.mark.parametrize(
#     "reply_packet", [b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n"]
# )
# def test_read_reply_packet(mock_socket, reply_packet):
#     mock_socket.recv.return_value = reply_packet
#     parser = ReplyPacketParser(mock_socket)
#     parser.read()
#
#     retrieved_packet = parser.feed()
#
#     mock_socket.recv.assert_called_with(ReplyPacketParser.BUFFER_LENGTH)
#     assert reply_packet == retrieved_packet.encode(ENCODING)
#
#
# @pytest.mark.skip(reason="Not working")
# @pytest.mark.parametrize("reply_packet", [b"INVALID PACKET"])
# def test_read_reply_packet_socket_timeout(mock_lirc, reply_packet):
#     with pytest.raises(LircdSocketTimeoutError):
#         mock_lirc.socket.recv.return_value = reply_packet
#         ReplyPacketParser.read(mock_lirc.socket)
#
#
# @pytest.mark.parametrize(
#     "reply_packet, data, exception",
#     [
#         (b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n", [], None,),
#         # ("INVALID PACKET", [], LircdInvalidReplyPacketError),
#         (
#             b"BEGIN\nSEND_ONCE remote key\nERROR\nINVALID\n",
#             [],
#             LircdInvalidReplyPacketError,
#         ),
#         (
#             b"BEGIN\nSEND_ONCE remote key\nERROR\nDATA\n1\nunknown remote: remote\n",
#             ["unknown remote: remote"],
#             LircdCommandFailureError,
#         ),
#         (
#             b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nDATA\n3\nraa\nblah\nbhal\n",
#             ["raa", "blah", "bhal"],
#             None,
#         ),
#     ],
# )
# def test_parse_reply_packet(mock_socket, reply_packet, data, exception):
#     mock_socket.recv.return_value = reply_packet
#     parser = ReplyPacketParser(mock_socket)
#
#     if exception:
#         with pytest.raises(exception):
#             parser.read()
#             parser.feed()
#     else:
#         parser.read()
#         assert parser.feed() == data
