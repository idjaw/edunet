import socket
import threading
from time import sleep

error_count = 0


def send_requests(call_number):
    global error_count
    # Connect to the server
    server_address = ('127.0.0.1', 9999)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    try:
        # Send a simple HTTP GET request
        request = b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: " + str(call_number).encode() + b"\r\n\r\n"
        client_socket.sendall(request)

        # Receive and print the server's response
        response = client_socket.recv(4096)
        print("Received response:", response.decode())
    except Exception as e:
        print(f"fail {e}")
        error_count += 1
    finally:
        # Close the client socket
        client_socket.close()

# Number of concurrent connections to create
num_connections = 500

# Create threads to send requests concurrently
threads = []
for i in range(num_connections):
    #sleep(0.08)
    thread = threading.Thread(target=send_requests, args=(i,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

print(error_count)
