from abc import ABC, abstractmethod


class ConnectionHandler(ABC):
    """
    Interface for implementing a connection handler used by the TCPListener
    """

    @abstractmethod
    def handle_connection(self, *args, **kwargs):
        """
        This provides the interface that has to be implemented that will be used by the
        TCPListener. The main idea is that a connection handler is provided to the
        TCPListener to handle the socket data as at comes in.

        As an example, you can implement a wsgi handler to handle connections.

        class WSGIHandler(ConnectionHandler):
            def handle_connection(foo, bar):
                pass
        """
