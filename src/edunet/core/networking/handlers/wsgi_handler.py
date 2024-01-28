import socket

from core.networking.handlers.connection_handler import ConnectionHandler


class WSGIHandler(ConnectionHandler):
    def handle_connection(self, client_socket: socket.socket):
        pass
