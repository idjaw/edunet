from unittest.mock import Mock, patch

import pytest

from core.networking.handlers.simple_http_connection_handler import (
    SimpleHTTPConnectionHandler,
)
from models.http import HTTPRequest, HTTPResponse


def test_http_connection_handler_initialization_success(mock_application):

    tcp_listener = SimpleHTTPConnectionHandler(mock_application)

    assert tcp_listener.application is mock_application


@patch(
    "core.networking.handlers.simple_http_connection_handler.HTTPRequest",
    spec=HTTPRequest,
)
def test_handle_connection_dispatches_request_and_sends_back_successfully(
    mock_http_request, simple_http_connection_handler, mock_socket
):
    # Given request data and client socket
    http_request = (
        b"GET / HTTP/1.1"
        + b"\r\nHost: localhost:8080\r\nUser-Agent: curl/7.58.0\r\n"
        + b"Accept: */*\r\n\r\n"
    )
    http_response_bytes = (
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
        + b"Content-Length: 13\r\nConnection: close\r\n\r\n"
        + b"Hello, world!"
    )

    mock_request_obj = Mock(
        method=b"GET",
        uri=b"/",
        version=b"HTTP/1.1",
        headers=b"Host: localhost:8080\r\nUser-Agent: curl/7.58.0\r\nAccept: */*",
        body=b"",
        spec=HTTPRequest,
    )
    mock_http_request.from_bytes.return_value = mock_request_obj
    mock_http_response = Mock(spec=HTTPResponse)
    mock_http_response.to_bytes.return_value = http_response_bytes
    simple_http_connection_handler.application.handle_request.return_value = (
        mock_http_response
    )

    # When I call handle_request
    res = simple_http_connection_handler.handle_connection(http_request, mock_socket)

    # Then I expect my response to be a bytes HTTP response
    assert res == http_response_bytes

    # Then I expect my methods to be called as such
    simple_http_connection_handler.application.handle_request.assert_called_once_with(
        mock_request_obj
    )
    mock_http_request.from_bytes.assert_called_once_with(http_request)
    mock_http_response.to_bytes.assert_called_once_with()


@patch(
    "core.networking.handlers.simple_http_connection_handler.HTTPRequest",
    spec=HTTPRequest,
)
def test_when_handle_request_fails_then_raise_the_same_exception(
    mock_http_request, simple_http_connection_handler, mock_socket
):
    # Given valid request data
    http_request = (
        b"GET / HTTP/1.1"
        + b"\r\nHost: localhost:8080\r\nUser-Agent: curl/7.58.0\r\n"
        + b"Accept: */*\r\n\r\n"
    )
    mock_request_obj = Mock(
        method=b"GET",
        uri=b"/",
        version=b"HTTP/1.1",
        headers=b"Host: localhost:8080\r\nUser-Agent: curl/7.58.0\r\nAccept: */*",
        body=b"",
        spec=HTTPRequest,
    )
    mock_http_request.from_bytes.return_value = mock_request_obj
    mock_http_response = Mock(spec=HTTPResponse)
    simple_http_connection_handler.application.handle_request.side_effect = Exception(
        "Bad stuff"
    )

    # When I call handle_connection
    # Then I expect an exception to be raised
    with pytest.raises(Exception, match="Bad stuff"):
        simple_http_connection_handler.handle_connection(http_request, mock_socket)

    # Then I expect my methods to behave as such
    simple_http_connection_handler.application.handle_request.assert_called_once_with(
        mock_request_obj
    )
    mock_http_request.from_bytes.assert_called_once_with(http_request)
    mock_http_response.to_bytes.assert_not_called()


@patch(
    "core.networking.handlers.simple_http_connection_handler.HTTPRequest",
    spec=HTTPRequest,
)
def test_when_http_request_from_bytes_fails_then_raise_the_same_exception(
    mock_http_request, simple_http_connection_handler, mock_socket
):
    # Given valid request data
    http_request = (
        b"GET / HTTP/1.1"
        + b"\r\nHost: localhost:8080\r\nUser-Agent: curl/7.58.0\r\n"
        + b"Accept: */*\r\n\r\n"
    )
    mock_http_request.from_bytes.side_effect = Exception("Bad stuff")
    mock_http_response = Mock(spec=HTTPResponse)

    # When I call handle_connection
    # Then I expect an exception to be raised
    with pytest.raises(Exception, match="Bad stuff"):
        simple_http_connection_handler.handle_connection(http_request, mock_socket)

    # Then I expect my methods to behave as such
    simple_http_connection_handler.application.handle_request.assert_not_called()
    mock_http_request.from_bytes.assert_called_once_with(http_request)
    mock_http_response.to_bytes.assert_not_called()


@patch(
    "core.networking.handlers.simple_http_connection_handler.HTTPRequest",
    spec=HTTPRequest,
)
def test_when_http_response_to_bytes_fails_then_raise_the_same_exception(
    mock_http_request, simple_http_connection_handler, mock_socket
):
    # Given valid request data
    http_request = (
        b"GET / HTTP/1.1"
        + b"\r\nHost: localhost:8080\r\nUser-Agent: curl/7.58.0\r\n"
        + b"Accept: */*\r\n\r\n"
    )
    mock_request_obj = Mock(
        method=b"GET",
        uri=b"/",
        version=b"HTTP/1.1",
        headers=b"Host: localhost:8080\r\nUser-Agent: curl/7.58.0\r\nAccept: */*",
        body=b"",
        spec=HTTPRequest,
    )
    mock_http_request.from_bytes.return_value = mock_request_obj
    mock_http_response = Mock(spec=HTTPResponse)
    mock_http_response.to_bytes.side_effect = Exception("Bad stuff")
    simple_http_connection_handler.application.handle_request.return_value = (
        mock_http_response
    )

    # When I call handle_connection
    # Then I expect an exception to be raised
    with pytest.raises(Exception, match="Bad stuff"):
        simple_http_connection_handler.handle_connection(http_request, mock_socket)

    # Then I expect my methods to behave as such
    simple_http_connection_handler.application.handle_request.assert_called_once_with(
        mock_request_obj
    )
    mock_http_request.from_bytes.assert_called_once_with(http_request)
    mock_http_response.to_bytes.assert_called_once_with()
