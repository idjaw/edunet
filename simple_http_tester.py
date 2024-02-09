import logging

from core.applications.simple_http_application import SimpleHTTPApplication
from core.networking.handlers.simple_http_connection_handler import (
    SimpleHTTPConnectionHandler,
)
from core.networking.listeners.tcp_listener import TCPListener
from core.nodes.simple_http_node import SimpleHTTPNode

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # Instantiate an HTTP application
    http_application = SimpleHTTPApplication()
    # Wrap the HTTP application with a Connection Handler
    http_connection_handler = SimpleHTTPConnectionHandler(http_application)
    # Wrap the Connection handler with a TCP Listener
    tcp_server = TCPListener("127.0.0.1", 9999, http_connection_handler)

    http_node = SimpleHTTPNode(tcp_server)

    # Start the listener to start allowing communication to your application
    http_node.start()
