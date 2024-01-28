from unittest import mock

import pytest

from exceptions import HTTPValidationError, HTTPDataModelError
from models.http import HTTPRequest, HTTPResponse


def test_http_response_model_converts_get_call_from_bytes_successfully():
    response_model = HTTPResponse(
        status_code=200,
        status_text="OK",
        body="Hello World",
        http_version="HTTP/1.1",
        content_type=None,
        additional_headers=None,
    )

    response_bytes = response_model.to_bytes()

    assert response_bytes == b"HTTP/1.1 200 OK\r\nContent-Length: 11\r\n\r\nHello World"


def test_http_response_model_converts_get_call_from_bytes_successfully_with_content_type():
    response_model = HTTPResponse(
        status_code=200,
        status_text="OK",
        body="Hello World",
        http_version="HTTP/1.1",
        content_type="text/html",
        additional_headers=None,
    )

    response_bytes = response_model.to_bytes()

    assert (
        response_bytes
        == b"HTTP/1.1 200 OK\r\nContent-Length: 11\r\nContent-Type: text/html\r\n\r\nHello World"
    )


def test_http_response_model_converts_get_call_from_bytes_successfully_with_additional_headers():
    response_model = HTTPResponse(
        status_code=200,
        status_text="OK",
        body="Hello World",
        http_version="HTTP/1.1",
        content_type="text/html",
        additional_headers={"a": "b", "c": "d"},
    )

    response_bytes = response_model.to_bytes()

    assert (
        response_bytes
        == b"HTTP/1.1 200 OK\r\nContent-Length: 11\r\nContent-Type: text/html\r\na: b\r\nc: d\r\n\r\nHello World"
    )


def test_http_response_model_raises_on_attribute_exception_failure():
    response_model = HTTPResponse(
        status_code=200,
        status_text="OK",
        body="Hello World",
        http_version="HTTP/1.1",
        content_type="text/html",
        additional_headers=["hi"],
    )

    with pytest.raises(
        HTTPDataModelError,
        match="Error creating response message: 'list' object has no attribute 'items'",
    ):
        response_model.to_bytes()


def test_http_response_model_raises_on_typeerror_exception_failure():
    response_model = HTTPResponse(
        status_code=200,
        status_text="OK",
        body=b"Hello World",
        http_version="HTTP/1.1",
        content_type="text/html",
        additional_headers=None,
    )

    with pytest.raises(
        HTTPDataModelError,
        match="Error creating response message: 'bytes' object has no attribute 'encode'",
    ):
        response_model.to_bytes()
