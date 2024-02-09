from unittest.mock import Mock

import pytest

from edunet.core.applications.simple_http_application import SimpleHTTPApplication
from edunet.models.http import HTTPRequest


@pytest.fixture
def mock_http_request_model():
    return Mock(spec=HTTPRequest)


@pytest.fixture
def simple_http_application():
    return SimpleHTTPApplication()
