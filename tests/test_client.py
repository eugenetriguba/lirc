# from unittest import mock
#
# import pytest
#
# from lirc import Client
# from lirc.connection.default_address import DefaultAddress
# from lirc.connection.default_socket import DefaultSocket


# @mock.patch("socket.socket")
# @mock.patch("platform.system")
# @pytest.mark.parametrize("os_name", ["WINDOWS", "DARWIN", "LINUX"])
# def test_default_lirc_initialization(mocked_system, mocked_socket, os_name):
#     mocked_system.return_value = os_name
#     expected_socket = DefaultSocket[os_name].value
#     expected_address = DefaultAddress[os_name].value
#
#     Client()
#     # lirc_socket = lirc.socket
#
#     assert mocked_socket.family == expected_socket.family
#     assert mocked_socket.type == expected_socket.type
#     mocked_socket.connect.assert_called_with(expected_address)
#     mocked_socket.settimeout.assert_called_with(5.0)
#
#
# def test_custom_lirc_initialization(mock_socket):
#     CUSTOM_ADDRESS = "CUSTOM"
#     CUSTOM_TIMEOUT = 10.0
#
#     Client(socket=mock_socket, address=CUSTOM_ADDRESS, timeout=CUSTOM_TIMEOUT)
#
#     mock_socket.connect.assert_called_with(CUSTOM_ADDRESS)
#     mock_socket.settimeout.assert_called_with(CUSTOM_TIMEOUT)


# @pytest.mark.parametrize(
#     "reply_packet, repeat_count",
#     [
#         (b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n", 1),
#         # (b"BEGIN\nSEND_ONCE remote key\nERROR\nEND\n", 1),
#         # (b"BEGIN\nSEND_ONCE remote key\nSUCCESS\nEND\n", 5),
#     ],
# )
# def test_send_once(mock_lirc, reply_packet, repeat_count):
#     REMOTE = "remote"
#     KEY = "key"
#     COMMAND = f"SEND_ONCE {REMOTE} {KEY}"
#     mock_lirc.socket.recv.return_value = reply_packet
#
#     response = mock_lirc.send(KEY, REMOTE, repeat_count=repeat_count)
#
#     mock_lirc.socket.sendall.assert_called_with((COMMAND + "\n").encode(ENCODING))
#
#
#     if repeat_count > 1:
#         assert type(response) == list
#         assert len(response) == repeat_count
#
#         for r in response:
#             _ensure_lirc_response(r, COMMAND)
#     else:
#         _ensure_lirc_response(response, COMMAND)
#
#
# def _ensure_lirc_response(response: LircResponse, command: str, data: list = []):
#     assert type(response) == LircResponse
#     assert response.command == command
#     assert response.data == data
