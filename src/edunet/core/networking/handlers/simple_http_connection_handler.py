import logging
import socket

from core.applications.application import Application
from core.networking.handlers.connection_handler import ConnectionHandler
from models.http import HTTPRequest

logger = logging.getLogger(__name__)


class SimpleHTTPConnectionHandler(ConnectionHandler):
    def __init__(self, application: Application):
        self.application = application

    def handle_connection(self, data: bytes, client_socket: socket.socket) -> bytes:
        return self.application.handle_request(HTTPRequest.from_bytes(data)).to_bytes()
