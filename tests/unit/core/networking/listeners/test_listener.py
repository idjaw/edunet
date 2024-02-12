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

    """
    Please note: Python 3.12 seems to have changed the assertion message being raised so
    previous versions are using one set of wording, and Python 3.12 another.

    Tests will match on a substring instead

    E       AssertionError: Regex pattern did not match.
    E        Regex: "Can't instantiate abstract class MyTestListener with abstract methods 
                    start, stop"
    E        Input: "Can't instantiate abstract class MyTestListener without an implementation 
                    for abstract methods 'handle_request', 'start', 'stop'"
    """
    with pytest.raises(TypeError) as exc:
        MyTestListener().start()

    assert all(s in str(exc.value) for s in ["handle_request", "start", "stop"])
