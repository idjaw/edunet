import pytest

from core.networking.handlers.connection_handler import ConnectionHandler


def test_instantiating_an_implemented_connection_handler_is_successful():
    class MyTestHandler(ConnectionHandler):
        def handle_connection(self, *args, **kwargs):
            return True

    my_test_listener = MyTestHandler()

    assert getattr(my_test_listener, "handle_connection")() is True


def test_connection_handler_raises_when_methods_not_implemented():
    class MyTestConnectionHandler(ConnectionHandler):
        pass

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class MyTestConnectionHandler "
        "with abstract method handle_connection",
    ):
        MyTestConnectionHandler().handle_connection()
