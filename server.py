import socket
import threading

# Handle client connections
def handle_client(client_socket):
    try:
        # Receive request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {request}")

        # Respond with a dummy message
        response = "018 OK dummy response"
        client_socket.send(response.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()

# Server setup
def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Start server
if __name__ == "__main__":
    start_server('localhost', 51234)
