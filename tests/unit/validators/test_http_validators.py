import string

import pytest
from hypothesis import given, strategies as st

from exceptions import HTTPValidationError
from validators.http_validators import validate_and_get_http_request_components


@st.composite
def http_request_strategy(draw):
    method = draw(st.sampled_from(["GET", "POST", "DELETE", "PUT"]))
    path = draw(
        st.text(min_size=1, alphabet=string.ascii_letters + string.digits + "/")
    )
    http_version = draw(st.sampled_from(["HTTP/1.0", "HTTP/1.1", "HTTP/2.0"]))

    headers = ""
    expected_headers_dict = {}
    for _ in range(draw(st.integers(min_value=0, max_value=10))):
        header_name = draw(
            st.text(min_size=1, alphabet=string.ascii_letters + string.digits + "-_")
        )
        header_value = draw(
            st.text(
                min_size=1,
                alphabet=string.printable.replace("\r", "").replace("\n", ""),
            )
        )
        headers += f"{header_name}: {header_value}\r\n"
        expected_headers_dict[f"{header_name}".encode()] = f"{header_value}".encode()

    # Define the expected result tuple
    request_line = f"{method} {path} {http_version}".encode()
    expected_result = (request_line, expected_headers_dict, b"")

    request = f"{method} {path} {http_version}\r\n{headers}\r\n"
    return request.encode(), expected_result


@pytest.mark.parametrize(
    "input_request, expected_result",
    [
        (
            b"GET /index.html HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\n",
            (
                b"GET /index.html HTTP/1.1",
                {
                    b"Host": b"www.example.com",
                    b"User-Agent": b"Mozilla/5.0",
                    b"Accept": b"text/html",
                },
                b"",
            ),
        ),
        (
            b'POST /api/update HTTP/1.1\r\nHost: www.example.com\r\nContent-Type: application/json\r\nContent-Length: 32\r\nUser-Agent: Mozilla/5.0\r\nAccept-Language: en-US\r\n\r\n{"key": "value"}',
            (
                b"POST /api/update HTTP/1.1",
                {
                    b"Host": b"www.example.com",
                    b"Content-Type": b"application/json",
                    b"Content-Length": b"32",
                    b"User-Agent": b"Mozilla/5.0",
                    b"Accept-Language": b"en-US",
                },
                b'{"key": "value"}',
            ),
        ),
    ],
)
def test_validate_http_request_is_successful(input_request, expected_result):
    assert validate_and_get_http_request_components(input_request) == expected_result


@pytest.mark.parametrize(
    "input_request, expected_result",
    [
        (
            b"get /index.html HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\n",
            f"Invalid request line pattern: b'get /index.html HTTP/1.1'",
        ),  # Case-insensitive method
        (
            b"GET /index HTTP/3.2\r\nHost: www.example.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\n",
            f"Invalid request line pattern: b'GET /index HTTP/3.2'",
        ),  # Incorrect HTTP version
        (
            b"GET /index.html HTTP/1.1\r\nInvalid Header\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\n",
            f"Invalid header pattern: b'Invalid Header'",
        ),  # Incorrect Header format
        (
            b"INVALID_REQUEST",
            f"Invalid request line pattern: b'INVALID_REQUEST'",
        ),  # Invalid format
    ],
)
def test_validate_http_request_raises(input_request, expected_result):
    with pytest.raises(HTTPValidationError, match=expected_result):
        validate_and_get_http_request_components(input_request)


@given(http_request_strategy())
def test_validate_http_request_strategy(request_input):
    res = validate_and_get_http_request_components(request_input[0])

    # From our defined strategy, the first argument was the input to calling our method
    # The second is the expected tuple result to ensure that we not only validated,
    # but we also split it up as expected
    assert res == request_input[1]
