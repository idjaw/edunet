import pytest as pytest

from edunet.core.networking.listeners.listener import Listener


@pytest.mark.parametrize(
    "method_name", ["accept_connection", "handle_request", "start", "stop"]
)
def test_instantiating_an_implemented_listener_is_successful(method_name):
    class MyTestListener(Listener):
        def accept_connection(self, *args, **kwargs):
            return True

        def handle_request(self, *args, **kwargs):
            return True

        def start(self, *args, **kwargs):
            return True

        def stop(self, *args, **kwargs):
            return True

    my_test_listener = MyTestListener()

    assert getattr(my_test_listener, method_name)() is True


def test_listener_raises_when_methods_not_implemented():
    class MyTestListener(Listener):
        pass

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class MyTestListener with abstract methods"
        " accept_connection, handle_request, start, stop",
    ):
        MyTestListener().start()
