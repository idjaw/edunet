from unittest.mock import Mock

import pytest

from core.networking.listeners.listener import Listener
from core.nodes.simple_http_node import SimpleHTTPNode


@pytest.fixture
def simple_http_node():
    return SimpleHTTPNode(Mock(spec=Listener))
