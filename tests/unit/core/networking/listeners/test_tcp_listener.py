import socket
import threading
from unittest.mock import patch, PropertyMock

import pytest

from edunet.core.networking.listeners.tcp_listener import TCPListener
from edunet.exceptions import TCPListenerError


def test_tcp_listener_initialization_success(mock_connection_handler, mock_socket):

    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)

    assert tcp_listener.hostname == "localhost"
    assert tcp_listener.port == 8080
    assert tcp_listener.is_listening is False
    assert tcp_listener.connection_handler is mock_connection_handler

    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_socket.return_value.bind.assert_called_once_with(("localhost", 8080))


def test_tcp_listener_initialization_failure(mock_connection_handler, mock_socket):
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.bind.side_effect = OSError("Failed to bind")

    with pytest.raises(OSError, match="Failed to bind"):
        TCPListener("localhost", 8080, mock_connection_handler)


@patch.object(TCPListener, "accept_connection")
def test_tcp_listener_start(mock_accept_connection, mock_connection_handler, caplog):
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    tcp_listener.start()

    assert tcp_listener.is_listening is True
    assert "Starting service." in caplog.text
    assert "Service listening on localhost:8080" in caplog.text
    mock_accept_connection.assert_called_once_with()


def test_tcp_listener_start_failure(mock_connection_handler, mock_socket, caplog):
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.listen.side_effect = Exception("Socket bind failed")

    with pytest.raises(
        TCPListenerError, match="Could not start service: Socket bind failed"
    ) as e_info:
        tcp_listener.start()

    assert "Socket bind failed" in str(e_info.value)
    assert "Could not start service: Socket bind failed" in caplog.text


def test_tcp_listener_start_already_listening(mock_connection_handler, caplog):
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    tcp_listener._is_listening = True
    tcp_listener.start()
    assert "Starting service." not in caplog.text
    assert "Service already starting. Nothing to do" in caplog.text


def test_tcp_listener_stop_success(mock_connection_handler, mock_socket, caplog):
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    mock_socket_instance = mock_socket.return_value
    tcp_listener._is_listening = True

    tcp_listener.stop()

    assert tcp_listener.is_listening is False
    assert mock_socket_instance.close.call_count == 1
    assert "Stopping service" in caplog.text
    assert "All threads terminated. Service has been stopped." in caplog.text


def test_tcp_listener_stop_already_stopped(mock_connection_handler, caplog):
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    tcp_listener._is_listening = False

    tcp_listener.stop()

    assert "Stopping service" in caplog.text
    assert "Service is already stopped. Nothing to do." in caplog.text


def test_tcp_listener_stop_failure(mock_connection_handler, mock_socket):
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.close.side_effect = Exception("Socket close failed")
    tcp_listener._is_listening = True

    with pytest.raises(TCPListenerError) as e_info:
        tcp_listener.stop()

    assert "Error shutting down service: Socket close failed" in str(e_info.value)


@patch.object(socket, "socket", spec=socket.socket)
@patch.object(threading, "Thread", spec=threading.Thread)
def test_accept_connection_success(mock_thread, mock_socket, tcp_listener, caplog):
    # Given a successful client connection
    tcp_listener.server_socket.accept.return_value = (mock_socket, "some address")
    mock_socket.recv.return_value = "some data"

    # When the accept_connection is called
    tcp_listener.accept_connection()

    # Then I expect my logging to behave as such
    assert "Connection established." in caplog.text
    assert f"The socket client: {mock_socket}" in caplog.text
    assert f"Error handling client socket: Bad things" not in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.server_socket.accept.assert_called_once_with()
    mock_socket.recv.assert_called_once_with(1024)
    mock_thread.assert_called_with(
        target=tcp_listener.handle_request, args=("some data", mock_socket)
    )
    mock_thread.return_value.start.assert_called_once_with()


@patch.object(socket, "socket", spec=socket.socket)
@patch.object(threading, "Thread", spec=threading.Thread)
def test_accept_connection_raises_if_service_was_not_started(
    mock_thread, mock_socket, mock_connection_handler, caplog
):
    # Given a failed client connection
    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)

    with pytest.raises(
        RuntimeError, match="Service is not running. Please start service."
    ):
        # When the accept_connection is called
        tcp_listener.accept_connection()

    # Then I expect my logging to behave as such
    assert "Connection established." not in caplog.text
    assert f"The socket client: {mock_socket}" not in caplog.text
    assert f"Error handling client socket: Bad things" not in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.server_socket.accept.assert_not_called()
    mock_socket.recv.assert_not_called()
    mock_thread.assert_not_called()
    mock_thread.return_value.start.assert_not_called()


@patch.object(socket, "socket", spec=socket.socket)
@patch.object(threading, "Thread", spec=threading.Thread)
def test_accept_connection_logs_warning_and_breaks_loop_if_client_connection_fails_and_listening_is_false(
    mock_thread, mock_socket, tcp_listener, caplog
):
    # Given a failed client connection
    tcp_listener.server_socket.accept.side_effect = Exception("Bad things")
    mock_socket.recv.return_value = "some data"

    # When the accept_connection is called
    tcp_listener.accept_connection()

    # Then I expect my logging to behave as such
    assert "Connection established." not in caplog.text
    assert f"The socket client: {mock_socket}" not in caplog.text
    assert f"Service stopped while accepting connections." in caplog.text
    assert f"Error handling client socket: Bad things" not in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.server_socket.accept.assert_called_once_with()
    mock_socket.recv.assert_not_called()
    mock_thread.assert_not_called()
    mock_thread.return_value.start.assert_not_called()


@patch.object(socket, "socket", spec=socket.socket)
@patch.object(threading, "Thread", spec=threading.Thread)
def test_accept_connection_logs_warning_and_continues_to_listen_if_client_connection_fails(
    mock_thread, mock_socket, mock_connection_handler, caplog
):
    # We want to limit to a single loop to break the while True
    sentinel = PropertyMock(
        side_effect=[
            False,  # Set for first instantiation as side_effect will be called
            True,  # Set for making sure it passes an initial active check
            True,  # Allows it to enter the while loop
            True,  # Allows it to simulate still listening inside the exception
            False,  # Does not allow it to continue back in to the loop
        ]
    )
    TCPListener._is_listening = sentinel

    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    # Given a failed client connection
    tcp_listener.server_socket.accept.side_effect = Exception("Bad things")
    mock_socket.recv.return_value = "some data"

    # When the accept_connection is called
    tcp_listener.accept_connection()

    # Then I expect my logging to behave as such
    assert "Connection established." not in caplog.text
    assert f"The socket client: {mock_socket}" not in caplog.text
    assert f"Service stopped while accepting connections." not in caplog.text
    assert f"Error handling client socket: Bad things" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.server_socket.accept.assert_called_once_with()
    mock_socket.recv.assert_not_called()
    mock_thread.assert_not_called()
    mock_thread.return_value.start.assert_not_called()


@patch.object(socket, "socket", spec=socket.socket)
@patch.object(threading, "Thread", spec=threading.Thread)
def test_accept_connection_logs_warning_and_continues_to_listen_if_receiving_socket_data_fails(
    mock_thread, mock_socket, mock_connection_handler, caplog
):
    # We want to limit to a single loop to break the while True
    sentinel = PropertyMock(
        side_effect=[
            False,  # Set for first instantiation as side_effect will be called
            True,  # Set for making sure it passes an initial active check
            True,  # Allows it to enter the while loop
            True,  # Allows it to simulate still listening inside the exception
            False,  # Does not allow it to continue back in to the loop
        ]
    )
    TCPListener._is_listening = sentinel

    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)

    # Given a failure to receive socket data
    tcp_listener.server_socket.accept.return_value = (mock_socket, "some address")
    mock_socket.recv.side_effect = Exception("Bad things")

    # When the accept_connection is called
    tcp_listener.accept_connection()

    # Then I expect my logging to behave as such
    assert "Connection established." in caplog.text
    assert f"The socket client: {mock_socket}" not in caplog.text
    assert f"Error handling client socket: Bad things" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.server_socket.accept.assert_called_once_with()
    mock_socket.recv.assert_called_once_with(1024)
    mock_thread.assert_not_called()
    mock_thread.return_value.start.assert_not_called()


@patch.object(socket, "socket", spec=socket.socket)
@patch.object(threading, "Thread", spec=threading.Thread)
def test_accept_connection_logs_warning_and_continues_to_listen_if_firing_off_thread_fails(
    mock_thread, mock_socket, mock_connection_handler, caplog
):
    # We want to limit to a single loop to break the while True
    sentinel = PropertyMock(
        side_effect=[
            False,  # Set for first instantiation as side_effect will be called
            True,  # Set for making sure it passes an initial active check
            True,  # Allows it to enter the while loop
            True,  # Allows it to simulate still listening inside the exception
            False,  # Does not allow it to continue back in to the loop
        ]
    )
    TCPListener._is_listening = sentinel

    tcp_listener = TCPListener("localhost", 8080, mock_connection_handler)
    # Given a failure to create thread
    tcp_listener.server_socket.accept.return_value = (mock_socket, "some address")
    mock_socket.recv.return_value = "some data"
    mock_thread.side_effect = Exception("Bad things")

    # When the accept_connection is called
    tcp_listener.accept_connection()

    # Then I expect my logging to behave as such
    assert "Connection established." in caplog.text
    assert f"The socket client: {mock_socket}" in caplog.text
    assert f"Error handling client socket: Bad things" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.server_socket.accept.assert_called_once_with()
    mock_socket.recv.assert_called_once_with(1024)
    mock_thread.assert_called_with(
        target=tcp_listener.handle_request, args=("some data", mock_socket)
    )
    mock_thread.return_value.start.assert_not_called()


@patch.object(socket, "socket", spec=socket.socket)
def test_handle_request_sends_data_back_to_client_successfully(
    mock_socket, tcp_listener, caplog
):
    # Given data being sent to a connection handler
    tcp_listener.connection_handler.handle_connection.return_value = (
        b"some response data"
    )
    mock_socket.fileno.return_value = -1

    # When the handle_request is called
    tcp_listener.handle_request(b"some_data", mock_socket)

    # Then I expect my logging to behave as such
    assert "Data to be sent back: b'some response data'" in caplog.text
    assert "Response sent back to client." in caplog.text
    assert "Could not send data" not in caplog.text
    assert "Closing connection" in caplog.text
    assert "Client socket closed successfully" in caplog.text
    assert "Client socket successfully closed" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.connection_handler.handle_connection.assert_called_once_with(
        b"some_data", mock_socket
    )
    mock_socket.sendall.assert_called_once_with(b"some response data")
    mock_socket.close.assert_called_once_with()
    mock_socket.fileno.assert_called_once_with()


@patch.object(socket, "socket", spec=socket.socket)
def test_handle_request_raises_when_raising_with_socket_error(
    mock_socket, tcp_listener, caplog
):
    # Given a failure from edunet.the connection_handler
    tcp_listener.connection_handler.handle_connection.side_effect = socket.error(
        "Bad stuff"
    )
    mock_socket.fileno.return_value = -1

    with pytest.raises(TCPListenerError, match="Bad stuff"):
        # When the handle_request is called
        tcp_listener.handle_request(b"some_data", mock_socket)

    # Then I expect my logging to behave as such
    assert "Data to be sent back: b'some response data'" not in caplog.text
    assert "Response sent back to client." not in caplog.text
    assert "Could not send data" in caplog.text
    assert "Closing connection" in caplog.text
    assert "Client socket closed successfully" in caplog.text
    assert "Client socket successfully closed" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.connection_handler.handle_connection.assert_called_once_with(
        b"some_data", mock_socket
    )
    mock_socket.sendall.assert_not_called()
    mock_socket.close.assert_called_once_with()
    mock_socket.fileno.assert_called_once_with()


@patch.object(socket, "socket", spec=socket.socket)
def test_handle_request_raises_when_sending_data_back_to_client_fails(
    mock_socket, tcp_listener, caplog
):
    # Given a failure to send data back to the client
    tcp_listener.connection_handler.handle_connection.return_value = (
        b"some response data"
    )
    mock_socket.sendall.side_effect = socket.error("Bad stuff")
    mock_socket.fileno.return_value = -1

    with pytest.raises(TCPListenerError, match="Bad stuff"):
        # When the handle_request is called
        tcp_listener.handle_request(b"some_data", mock_socket)

    # Then I expect my logging to behave as such
    assert "Data to be sent back: b'some response data'" in caplog.text
    assert "Response sent back to client." not in caplog.text
    assert "Could not send data" in caplog.text
    assert "Closing connection" in caplog.text
    assert "Client socket closed successfully" in caplog.text
    assert "Client socket successfully closed" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.connection_handler.handle_connection.assert_called_once_with(
        b"some_data", mock_socket
    )
    mock_socket.sendall.assert_called_once_with(b"some response data")
    mock_socket.close.assert_called_once_with()
    mock_socket.fileno.assert_called_once_with()


@patch.object(socket, "socket", spec=socket.socket)
def test_handle_request_logs_error_when_closing_client_socket_fails(
    mock_socket, tcp_listener, caplog
):
    # Given a failure to close the client socket
    tcp_listener.connection_handler.handle_connection.return_value = (
        b"some response data"
    )
    mock_socket.fileno.return_value = 5  # Anything that is not -1 and greater than 0
    mock_socket.close.side_effect = socket.error("Bad stuff")

    # When the handle_request is called
    tcp_listener.handle_request(b"some_data", mock_socket)

    # Then I expect my logging to behave as such
    assert "Data to be sent back: b'some response data'" in caplog.text
    assert "Response sent back to client." in caplog.text
    assert "Could not send data" not in caplog.text
    assert "Closing connection" in caplog.text
    assert "Socket error closing client socket: Bad stuff" in caplog.text
    assert "Client socket closed successfully" not in caplog.text
    assert "Client socket successfully closed" not in caplog.text
    assert "Socket not closed" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.connection_handler.handle_connection.assert_called_once_with(
        b"some_data", mock_socket
    )
    mock_socket.sendall.assert_called_once_with(b"some response data")
    mock_socket.close.assert_called_once_with()
    mock_socket.fileno.assert_called_once_with()


@patch.object(socket, "socket", spec=socket.socket)
def test_handle_request_logs_error_when_closing_client_socket_is_successful_but_socket_check_fails(
    mock_socket, tcp_listener, caplog
):
    # Given a failure to check the client socket is closed
    tcp_listener.connection_handler.handle_connection.return_value = (
        b"some response data"
    )
    mock_socket.fileno.return_value = 5  # Anything that is not -1 and greater than 0

    # When the handle_request is called
    tcp_listener.handle_request(b"some_data", mock_socket)

    # Then I expect my logging to behave as such
    assert "Data to be sent back: b'some response data'" in caplog.text
    assert "Response sent back to client." in caplog.text
    assert "Could not send data" not in caplog.text
    assert "Closing connection" in caplog.text
    assert "Socket error closing client socket:" not in caplog.text
    assert "Client socket closed successfully" in caplog.text
    assert "Client socket successfully closed" not in caplog.text
    assert "Socket not closed" in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.connection_handler.handle_connection.assert_called_once_with(
        b"some_data", mock_socket
    )
    mock_socket.sendall.assert_called_once_with(b"some response data")
    mock_socket.close.assert_called_once_with()
    mock_socket.fileno.assert_called_once_with()


@patch.object(socket, "socket", spec=socket.socket)
def test_handle_request_closes_socket_after_failing_once(
    mock_socket, tcp_listener, caplog
):
    # Given a failure to close the client socket but checking it is closed passes
    tcp_listener.connection_handler.handle_connection.return_value = (
        b"some response data"
    )
    mock_socket.close.side_effect = socket.error("Bad stuff")
    mock_socket.fileno.return_value = -1  # Anything that is not -1 and greater than 0

    # When the handle_request is called
    tcp_listener.handle_request(b"some_data", mock_socket)

    # Then I expect my logging to behave as such
    assert "Data to be sent back: b'some response data'" in caplog.text
    assert "Response sent back to client." in caplog.text
    assert "Could not send data" not in caplog.text
    assert "Closing connection" in caplog.text
    assert "Socket error closing client socket: Bad stuff" in caplog.text
    assert "Client socket closed successfully" not in caplog.text
    assert "Client socket successfully closed" in caplog.text
    assert "Socket not closed" not in caplog.text

    # Then I expect my methods to be called as such
    tcp_listener.connection_handler.handle_connection.assert_called_once_with(
        b"some_data", mock_socket
    )
    mock_socket.sendall.assert_called_once_with(b"some response data")
    mock_socket.close.assert_called_once_with()
    mock_socket.fileno.assert_called_once_with()
