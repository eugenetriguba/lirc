import socket
from unittest import mock

import pytest

from lirc import Lirc


@pytest.fixture
def mock_socket():
    return mock.Mock(spec=socket.socket)


@pytest.fixture
def mock_lirc(mock_socket):
    return Lirc(socket=mock_socket)


@pytest.fixture
def mock_lirc_and_socket(mock_lirc):
    return (mock_lirc, mock_lirc._Lirc__socket)
