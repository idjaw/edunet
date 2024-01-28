import logging
import re
from typing import Tuple, Dict

from exceptions import HTTPValidationError

# Compiled regex patterns for request line, headers, and body
REQUEST_LINE_PATTERN = re.compile(rb"^[A-Z]+ [^\r\n]* HTTP/(1\.[01]|2\.0)$")
HEADER_PATTERN = re.compile(rb"^[^\r\n]+: [^\r\n]*$")
BODY_PATTERN = re.compile(rb".*")

logger = logging.getLogger(__name__)


def validate_and_get_http_request_components(
    request: bytes,
) -> Tuple[bytes, Dict[bytes, bytes], bytes]:
    """
    Validates an HTTP request and returns its parts if valid.

    Args:
    - request (bytes): The HTTP request to validate.

    Returns:
    - tuple: A tuple containing the request line, headers, and body if the request
             is valid, otherwise None.
    """

    # Split the request into components, excluding empty lines
    request_line, headers, body = _get_parts(request)

    # Validate request line
    if not re.match(REQUEST_LINE_PATTERN, request_line):
        logger.error("Invalid request line: %s", request_line)
        raise HTTPValidationError(f"Invalid request line pattern: {request_line}")

    # Validate headers format and parse into key-value pairs
    parsed_headers = {}
    for header in headers:
        if not re.match(HEADER_PATTERN, header):
            logger.error("Invalid header pattern: %s", header)
            raise HTTPValidationError(f"Invalid header pattern: {header}")

        # Split header into key and value
        header_name, header_value = header.split(b": ", 1)
        parsed_headers[header_name] = header_value

    return request_line, parsed_headers, body


def _get_parts(request):
    # Split the request into components using line boundaries
    components = request.split(b"\r\n\r\n", 1)

    # Extract the request line and headers
    request_line_and_headers = components[0].split(b"\r\n")
    request_line = request_line_and_headers[0]
    headers = request_line_and_headers[1:]

    # Initialize the body
    body = b""

    # If there are components beyond the request line and headers
    if len(components) > 1:
        body = components[1]

    return request_line, headers, body
