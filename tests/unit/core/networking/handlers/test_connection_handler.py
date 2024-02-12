import pytest

from edunet.core.networking.handlers.connection_handler import ConnectionHandler


def test_instantiating_an_implemented_connection_handler_is_successful():
    class MyTestHandler(ConnectionHandler):
        def handle_connection(self, *args, **kwargs):
            return True

    my_test_listener = MyTestHandler()

    assert getattr(my_test_listener, "handle_connection")() is True


def test_connection_handler_raises_when_methods_not_implemented():
    class MyTestConnectionHandler(ConnectionHandler):
        pass

    """
    Please note: Python 3.12 seems to have changed the assertion message being raised so
    previous versions are using one set of wording, and Python 3.12 another.

    Tests will match on a substring instead

    E       AssertionError: Regex pattern did not match.
    E        Regex: "Can't instantiate abstract class MyTestConnectionHandler with abstract method 
                    handle_connection"
    E        Input: "Can't instantiate abstract class MyTestConnectionHandler without an implementation 
                    for abstract method 'handle_connection'"
    """
    with pytest.raises(TypeError) as exc:
        MyTestConnectionHandler().handle_connection()

    assert "handle_connection" in str(exc.value)
