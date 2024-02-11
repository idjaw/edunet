from unittest import mock

import pytest

from edunet.exceptions import HTTPValidationError, HTTPDataModelError
from edunet.models.http import HTTPRequest


@mock.patch("edunet.models.http.validate_and_get_http_request_components")
def test_http_request_model_converts_get_call_from_bytes_successfully(
    mock_validate_and_get_http_request_components,
):
    test_input = b"GET /index.html HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\n"

    mock_validate_and_get_http_request_components.return_value = (
        b"GET /index.html HTTP/1.1",
        {
            b"Host": b"www.example.com",
            b"User-Agent": b"Mozilla/5.0",
            b"Accept": b"text/html",
        },
        b"",
    )

    request_model = HTTPRequest.from_bytes(test_input)

    mock_validate_and_get_http_request_components.assert_called_once_with(test_input)

    assert request_model.headers == {
        b"Host": b"www.example.com",
        b"User-Agent": b"Mozilla/5.0",
        b"Accept": b"text/html",
    }
    assert request_model.method == b"GET"
    assert request_model.uri == b"/index.html"
    assert request_model.version == b"HTTP/1.1"
    assert request_model.body == b""


@mock.patch("edunet.models.http.validate_and_get_http_request_components")
def test_http_request_model_converts_post_call_with_body_from_bytes_successfully(
    mock_validate_and_get_http_request_components,
):
    test_input = b"GET /index.html HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\nHello World"

    mock_validate_and_get_http_request_components.return_value = (
        b"POST /index.html HTTP/1.1",
        {
            b"Host": b"www.example.com",
            b"User-Agent": b"Mozilla/5.0",
            b"Accept": b"text/html",
        },
        b"Hello World",
    )

    request_model = HTTPRequest.from_bytes(test_input)

    mock_validate_and_get_http_request_components.assert_called_once_with(test_input)

    assert request_model.headers == {
        b"Host": b"www.example.com",
        b"User-Agent": b"Mozilla/5.0",
        b"Accept": b"text/html",
    }
    assert request_model.method == b"POST"
    assert request_model.uri == b"/index.html"
    assert request_model.version == b"HTTP/1.1"
    assert request_model.body == b"Hello World"


@pytest.mark.parametrize("exc", [AttributeError, HTTPValidationError])
@mock.patch("edunet.models.http.validate_and_get_http_request_components")
def test_http_request_model_raises_on_failure(
    mock_validate_and_get_http_request_components, exc
):
    mock_validate_and_get_http_request_components.side_effect = exc("Bad Stuff")

    with pytest.raises(
        HTTPDataModelError, match="Error creating Request object: Bad Stuff"
    ):
        HTTPRequest.from_bytes(b"will fail")
