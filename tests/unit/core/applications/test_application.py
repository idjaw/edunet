import pytest

from edunet.core.applications.application import Application


def test_instantiating_an_implemented_application_is_successful():
    class MyTestApplication(Application):
        def handle_request(self, *args, **kwargs):
            return True

    my_test_application = MyTestApplication()

    assert getattr(my_test_application, "handle_request")() is True


def test_connection_handler_raises_when_methods_not_implemented():
    class MyTestApplication(Application):
        pass

    """
    Please note: Python 3.12 seems to have changed the assertion message being raised so
    previous versions are using one set of wording, and Python 3.12 another.

    Tests will match on a substring instead

    E       AssertionError: Regex pattern did not match.
    E        Regex: "Can't instantiate abstract class MyTestApplication with abstract methods 
                    start, stop"
    E        Input: "Can't instantiate abstract class MyTestApplication without an implementation 
                    for abstract methods 'start', 'stop'"
    """
    with pytest.raises(TypeError) as exc:
        MyTestApplication().handle_request("foo")  # type: ignore

    assert "handle_request" in str(exc.value)
