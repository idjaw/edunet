import pytest

from core.applications.application import Application


def test_instantiating_an_implemented_application_is_successful():
    class MyTestApplication(Application):
        def handle_request(self, *args, **kwargs):
            return True

    my_test_application = MyTestApplication()

    assert getattr(my_test_application, "handle_request")() is True


def test_connection_handler_raises_when_methods_not_implemented():
    class MyTestApplication(Application):
        pass

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class MyTestApplication "
        "with abstract method handle_request",
    ):
        MyTestApplication().handle_request("foo")  # type: ignore
