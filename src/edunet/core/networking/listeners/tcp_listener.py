import logging
import socket
import threading

from core.networking.handlers.connection_handler import ConnectionHandler
from core.networking.listeners.listener import Listener
from exceptions import TCPListenerError

logger = logging.getLogger(__name__)


class TCPListener(Listener):
    def __init__(self, hostname: str, port: int, connection_handler: ConnectionHandler):
        self.hostname = hostname
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.hostname, self.port))
        self._is_listening = False

        self.connection_handler = connection_handler

    @property
    def is_listening(self):
        """
        Read only property to check whether the TCPListener is listening and active.

        This is controlled internally through starting and stopping the service.
        e.g. tcp_listener.start() and tcp_listener.stop()
        """
        return self._is_listening

    def accept_connection(self) -> None:
        """
        This method will be used to accept incoming connections. It will only function
        if the service is running. Ensure the start_service() method is called first.
        An exception will be raised otherwise.
        """

        if not self.is_listening:
            raise RuntimeError("Service is not running. Please start service.")

        while self.is_listening:
            try:
                client_socket, _ = self.server_socket.accept()
                logger.info("Connection established.")

                request_data = client_socket.recv(1024)

                logger.info(f"The socket client: {client_socket}")

                threading.Thread(
                    target=self.handle_request, args=(request_data, client_socket)
                ).start()

                # We still want a safeguarded way to break the loop if we find ourselves
                # in a situation where the service goes down while hanging in this loop
                if not self.is_listening:
                    logger.warning("Detected service interruption. Exiting.")
                    break
            except Exception as e:
                # Handle case where the socket is closed while accepting connections
                if not self.is_listening:
                    logger.warning("Service stopped while accepting connections.")
                    break
                else:
                    logger.error(f"Error handling client socket: {e}")

    def handle_request(self, request_data, client_socket: socket.socket) -> None:
        """
        Provide a RequestData object to receive a ResponseData response.
        """
        try:
            res = self.connection_handler.handle_connection(request_data, client_socket)
            logger.info(f"Data to be sent back: {res}")
            client_socket.sendall(res)
            logger.info("Response sent back to client.")
        except socket.error as e:
            logger.error(f"Could not send data: {e}")
            raise TCPListenerError(e)
        finally:
            logger.info("Closing connection")
            self._close_client_socket(client_socket)

    def start(self) -> None:
        """
        Will start the TCPListener service to listen for incoming connections
        """
        try:
            if not self.is_listening:
                logger.info("Starting service.")
                self.server_socket.listen()
                self._is_listening = True

                logger.info(f"Service listening on {self.hostname}:{self.port}")

                self.accept_connection()
            else:
                logger.info("Service already starting. Nothing to do")
        except Exception as e:
            logger.error(f"Could not start service: {e}")
            raise TCPListenerError(f"Could not start service: {e}")

    def stop(self) -> None:
        """
        Will stop the TCPListener service and will no longer accept connections
        """
        logger.info("Stopping service")
        if self.is_listening:
            try:
                self.server_socket.close()
                self._is_listening = False
            except Exception as e:
                logger.error(f"Error shutting down service: {e}")
                raise TCPListenerError(f"Error shutting down service: {e}")

            logger.info("All threads terminated. Service has been stopped.")
        else:
            logger.warning("Service is already stopped. Nothing to do.")

    def _close_client_socket(self, client_socket) -> None:
        """
        Internal method to close a client socket and check if it has been closed
        """
        try:
            client_socket.close()
        except socket.error as e:
            logger.error(f"Socket error closing client socket: {e}")
        else:
            logger.info("Client socket closed successfully")
        finally:
            if client_socket.fileno() == -1:
                logger.info("Client socket successfully closed")
            else:
                logger.warning("Socket not closed")
