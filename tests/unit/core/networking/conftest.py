from unittest import mock
from unittest.mock import Mock, patch, PropertyMock

import pytest

from edunet.core.networking.handlers.connection_handler import ConnectionHandler
from edunet.core.networking.listeners.tcp_listener import TCPListener


@pytest.fixture
def mock_connection_handler():
    return Mock(spec=ConnectionHandler)


@pytest.fixture
def mock_socket():
    with patch("socket.socket", spec=True) as mock:
        yield mock


@pytest.fixture(scope="function")
def tcp_listener(mock_connection_handler, mock_socket):
    # We want to limit to a single loop to break the while True
    sentinel = PropertyMock(
        side_effect=[
            False,  # Set for first instantiation as side_effect will be called
            True,  # Set for making sure it passes an initial active check
            True,  # Allows it to enter the while loop
            False,  # Stops it after the first iteration
        ]
    )
    TCPListener._is_listening = sentinel

    listener = TCPListener("localhost", 8080, mock_connection_handler)

    # The following two lines are set because of an odd issue:
    # Even though the scope is explicitly set to function,
    # the property mock seems to still "leak" into the rest of the tests.
    # By yielding to return back after each test and ultimately "resetting"
    # the property to a default False value allows normal behaviour to work
    yield listener
    TCPListener._is_listening = False
