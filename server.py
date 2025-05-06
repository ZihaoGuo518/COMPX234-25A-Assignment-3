import socket
import threading

# Shared tuple space
tuple_space = {}
lock = threading.Lock()

# Handle client connections
def handle_client(client_socket):
    try:
        # Receive request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {request}")

        # Parse request
        request_parts = request.split()
        command = request_parts[1]
        key = request_parts[2]
        response = ""

        # Handle PUT, GET, READ
        with lock:
            if command == 'P':  # PUT operation
                value = request_parts[3]
                if key in tuple_space:
                    response = f"024 ERR {key} already exists"
                else:
                    tuple_space[key] = value
                    response = f"018 OK ({key}, {value}) added"
            elif command == 'R':  # READ operation
                if key in tuple_space:
                    response = f"018 OK ({key}, {tuple_space[key]}) read"
                else:
                    response = f"024 ERR {key} does not exist"
            elif command == 'G':  # GET operation
                if key in tuple_space:
                    value = tuple_space.pop(key)
                    response = f"018 OK ({key}, {value}) removed"
                else:
                    response = f"024 ERR {key} does not exist"
            else:
                response = "024 ERR Unknown command"

        # Send the response back to the client
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
