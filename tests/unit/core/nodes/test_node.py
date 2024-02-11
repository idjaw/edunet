from unittest.mock import Mock

import pytest

from edunet.core.networking.listeners.listener import Listener
from edunet.core.nodes.node import Node


def test_instantiating_an_implemented_node_is_successful():
    class MyNode(Node):
        def start(self, *args, **kwargs):
            return True

        def stop(self, *args, **kwargs):
            return True

    my_node = MyNode(Mock(spec=Listener))

    assert getattr(my_node, "start")() is True
    assert getattr(my_node, "stop")() is True


def test_node_raises_when_methods_not_implemented():
    class MyNode(Node):
        pass

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class MyNode "
        "with abstract methods start, stop",
    ):
        MyNode(Mock(spec=Listener)).start("foo")  # type: ignore
