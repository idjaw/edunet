import logging

from edunet.core.applications.application import Application
from edunet.models.http import HTTPRequest, HTTPResponse

logger = logging.getLogger(__name__)


class SimpleHTTPApplication(Application):

    def handle_request(self, request_data: HTTPRequest) -> HTTPResponse:
        """
        Provide a HTTPRequest object to receive a HTTPResponse object.
        """

        logger.info(f"Request data: {request_data}")

        try:
            return HTTPResponse(
                status_code=200,
                status_text="OK",
                body=f"Message received: {request_data}",
            )
        except (SyntaxError, TypeError, ValueError, AttributeError) as e:
            logger.error(f"Could not construct data: {e}")
            return HTTPResponse(
                status_code=500, status_text="Internal Server Error", body=""
            )
        except Exception as e:
            logger.exception(f"Unexpected server error: {e}")
            return HTTPResponse(
                status_code=500, status_text="Internal Server Error", body=""
            )
