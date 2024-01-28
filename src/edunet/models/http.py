import logging
from dataclasses import dataclass
from typing import Optional, Dict, TypeVar, Type

from exceptions import HTTPValidationError, HTTPDataModelError
from models.base_types import Request, Response
from validators.http_validators import (
    validate_and_get_http_request_components,
)

logger = logging.getLogger(__name__)


T = TypeVar("T", bound="HTTPRequest")


@dataclass
class HTTPRequest(Request):
    method: bytes
    uri: bytes
    version: bytes
    headers: Dict[bytes, bytes]
    body: bytes

    @classmethod
    def from_bytes(cls: Type[T], data: bytes) -> T:
        try:
            request_line, headers, body = validate_and_get_http_request_components(data)

            # Parse request line
            method, uri, version = request_line.split(b" ")

            return cls(
                method=method,
                uri=uri,
                version=version,
                headers=headers,
                body=body,
            )
        except (AttributeError, HTTPValidationError) as e:
            logger.error(f"Error creating Request object: {e}")
            raise HTTPDataModelError(f"Error creating Request object: {e}")


@dataclass
class HTTPResponse(Response):
    status_code: int
    status_text: str
    body: str
    http_version: str = "HTTP/1.1"
    content_type: Optional[str] = None
    additional_headers: Optional[dict] = None

    def to_bytes(self) -> bytes:
        try:
            # Construct status line
            status_line = (
                f"{self.http_version} {self.status_code} {self.status_text}\r\n".encode(
                    "utf-8"
                )
            )

            # Construct headers
            headers = f"Content-Length: {len(self.body)}\r\n".encode("utf-8")
            if self.content_type:
                headers += f"Content-Type: {self.content_type}\r\n".encode("utf-8")
            if self.additional_headers:
                for key, value in self.additional_headers.items():
                    headers += f"{key}: {value}\r\n".encode("utf-8")
            headers += b"\r\n"

            # Combine status line, headers, and body
            response = status_line + headers + self.body.encode("utf-8")
        except (AttributeError, TypeError) as e:
            logger.error(f"Error creating response message: {e}")
            raise HTTPDataModelError(f"Error creating response message: {e}")

        return response
