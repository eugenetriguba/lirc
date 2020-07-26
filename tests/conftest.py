import socket
from unittest import mock

import pytest

from lirc import Client, LircdConnection


@pytest.fixture
def mock_socket():
    return mock.MagicMock(spec=socket.socket)


@pytest.fixture
def mock_lirc(mock_socket):
    return Client(connection=LircdConnection(socket=mock_socket))
