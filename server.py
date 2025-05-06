import socket
import threading
import time

# Shared tuple space
tuple_space = {}
lock = threading.Lock()

# Statistics variables
total_operations = 0
total_puts = 0
total_gets = 0
total_reads = 0
total_errors = 0
total_clients = 0

# Handle client connections
def handle_client(client_socket):
    global total_operations, total_puts, total_gets, total_reads, total_errors

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
                    total_errors += 1
                else:
                    tuple_space[key] = value
                    response = f"018 OK ({key}, {value}) added"
                    total_puts += 1
            elif command == 'R':  # READ operation
                if key in tuple_space:
                    response = f"018 OK ({key}, {tuple_space[key]}) read"
                    total_reads += 1
                else:
                    response = f"024 ERR {key} does not exist"
                    total_errors += 1
            elif command == 'G':  # GET operation
                if key in tuple_space:
                    value = tuple_space.pop(key)
                    response = f"018 OK ({key}, {value}) removed"
                    total_gets += 1
                else:
                    response = f"024 ERR {key} does not exist"
                    total_errors += 1
            else:
                response = "024 ERR Unknown command"
                total_errors += 1

        # Send the response back to the client
        client_socket.send(response.encode('utf-8'))
        total_operations += 1

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()

# Periodically print server statistics
def print_statistics():
    while True:
        time.sleep(10)
        with lock:
            num_tuples = len(tuple_space)
            avg_tuple_size = sum(len(k) + len(v) for k, v in tuple_space.items()) / num_tuples if num_tuples > 0 else 0
            avg_key_size = sum(len(k) for k in tuple_space.keys()) / num_tuples if num_tuples > 0 else 0
            avg_value_size = sum(len(v) for v in tuple_space.values()) / num_tuples if num_tuples > 0 else 0

            print(f"\nServer Statistics: "
                  f"\n  Tuples: {num_tuples}, "
                  f"Avg Tuple Size: {avg_tuple_size:.2f}, "
                  f"Avg Key Size: {avg_key_size:.2f}, "
                  f"Avg Value Size: {avg_value_size:.2f}, "
                  f"\n  Total Clients: {total_clients}, "
                  f"Total Operations: {total_operations}, "
                  f"Total READs: {total_reads}, "
                  f"Total GETs: {total_gets}, "
                  f"Total PUTs: {total_puts}, "
                  f"Total ERRs: {total_errors}\n")

# Server setup
def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    # Start the statistics thread
    stats_thread = threading.Thread(target=print_statistics)
    stats_thread.daemon = True
    stats_thread.start()

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        global total_clients
        total_clients += 1
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Start server
if __name__ == "__main__":
    start_server('localhost', 51234)
