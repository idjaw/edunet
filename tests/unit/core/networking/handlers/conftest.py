from unittest.mock import Mock

import pytest

from edunet.core.applications.application import Application
from edunet.core.networking.handlers.simple_http_connection_handler import (
    SimpleHTTPConnectionHandler,
)


@pytest.fixture
def mock_application():
    return Mock(spec=Application)


@pytest.fixture
def simple_http_connection_handler(mock_application):
    return SimpleHTTPConnectionHandler(mock_application)
