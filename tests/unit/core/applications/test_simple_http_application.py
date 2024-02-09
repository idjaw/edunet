from unittest.mock import Mock, patch

import pytest

from models.http import HTTPRequest, HTTPResponse


@patch("core.applications.simple_http_application.HTTPResponse")
def test_handle_request_successfully_responds_back_with_valid_data(
    mock_http_response_model, simple_http_application, mock_http_request_model, caplog
):
    # Given request data and client socket
    mock_request_obj = Mock(
        method=b"GET",
        uri=b"/",
        version=b"HTTP/1.1",
        headers=b"Host: localhost:8080\r\nUser-Agent: curl/7.58.0\r\nAccept: */*",
        body=b"",
        spec=HTTPRequest,
    )

    mock_http_response_model.return_value = Mock(
        status_code=200,
        status_text="OK",
        body=f"Message received: {mock_request_obj}",
        spec=HTTPResponse,
    )

    # When I call handle_request
    res = simple_http_application.handle_request(mock_request_obj)

    # Then I expect my methods to be called as such
    assert res.status_code == 200
    assert res.status_text == "OK"
    assert res.body == f"Message received: {mock_request_obj}"

    assert f"Request data: {mock_request_obj}" in caplog.text


@patch("core.applications.simple_http_application.HTTPResponse")
@pytest.mark.parametrize(
    "exception_type", [SyntaxError, TypeError, ValueError, AttributeError]
)
def test_handle_request_returns_500_when_http_response_fails_to_craft_response(
    mock_http_response_model,
    simple_http_application,
    mock_http_request_model,
    caplog,
    exception_type,
):
    # Given request data and client socket
    mock_request_obj = Mock(
        method=b"GET",
        uri=b"/",
        version=b"HTTP/1.1",
        headers=b"Host: localhost:8080\r\nUser-Agent: curl/7.58.0\r\nAccept: */*",
        body=b"",
        spec=HTTPRequest,
    )

    mock_http_response_model.side_effect = exception_type("Bad stuff")

    # When I call handle_request
    # Then it raises
    with pytest.raises(exception_type, match="Bad stuff"):
        res = simple_http_application.handle_request(mock_request_obj)

        # Then I expect my methods to be called as such
        assert res.status_code == 500
        assert res.status_text == "Internal Server Error"
        assert res.body == ""

    assert f"Request data: {mock_request_obj}" in caplog.text
    assert f"Could not construct data: Bad stuff" in caplog.text
    assert f"Unexpected server error" not in caplog.text


@patch("core.applications.simple_http_application.HTTPResponse")
def test_handle_request_returns_500_logs_error_when_any_other_exception_occurs(
    mock_http_response_model, simple_http_application, mock_http_request_model, caplog
):
    # Given request data and client socket
    mock_request_obj = Mock(
        method=b"GET",
        uri=b"/",
        version=b"HTTP/1.1",
        headers=b"Host: localhost:8080\r\nUser-Agent: curl/7.58.0\r\nAccept: */*",
        body=b"",
        spec=HTTPRequest,
    )

    mock_http_response_model.side_effect = OSError("Bad stuff")

    # When I call handle_request
    # Then it raises
    with pytest.raises(OSError, match="Bad stuff"):
        res = simple_http_application.handle_request(mock_request_obj)

        # Then I expect my methods to be called as such
        assert res.status_code == 500
        assert res.status_text == "Internal Server Error"
        assert res.body == ""

    # Then I expect my methods to be called as such
    assert f"Request data: {mock_request_obj}" in caplog.text
    assert f"Could not construct data: Bad stuff" not in caplog.text
    assert f"Unexpected server error" in caplog.text
