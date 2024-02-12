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

    """
    Please note: Python 3.12 seems to have changed the assertion message being raised so
    previous versions are using one set of wording, and Python 3.12 another.
    
    Tests will match on a substring instead
    
    E       AssertionError: Regex pattern did not match.
    E        Regex: "Can't instantiate abstract class MyNode with abstract methods 
                    start, stop"
    E        Input: "Can't instantiate abstract class MyNode without an implementation 
                    for abstract methods 'start', 'stop'"
    """

    with pytest.raises(TypeError) as exc:
        MyNode(Mock(spec=Listener)).start("foo")  # type: ignore

    assert all(s in str(exc.value) for s in ["start", "stop"])
