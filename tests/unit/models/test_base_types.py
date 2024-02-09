from dataclasses import dataclass

from models.base_types import Request, Response


def test_implement_dataclass_from_request_base_type():
    @dataclass
    class MyDataModel(Request):
        foo: bytes
        bar: str

    my_data_model = MyDataModel(b"foo", "bar")

    assert my_data_model.foo == b"foo"
    assert my_data_model.bar == "bar"


def test_implement_dataclass_from_response_base_type():
    @dataclass
    class MyDataModel(Response):
        foo: bytes
        bar: str

    my_data_model = MyDataModel(b"foo", "bar")

    assert my_data_model.foo == b"foo"
    assert my_data_model.bar == "bar"
