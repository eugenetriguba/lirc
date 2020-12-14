import socket
from unittest import mock

import pytest

from lirc import Client, LircdConnection


@pytest.fixture
def mock_socket():
    return mock.MagicMock(spec=socket.socket)


@pytest.fixture
def mock_connection(mock_socket):
    return LircdConnection(socket=mock_socket)


@pytest.fixture
def mock_client(mock_connection):
    return Client(connection=mock_connection)


@pytest.fixture
def mock_client_and_connection(mock_connection):
    return Client(connection=mock_connection), mock_connection
