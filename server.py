import socket
import threading
import time
import json
import os
import logging

# Setup logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# File for persistent storage
tuple_space_file = "tuple_space.json"

# Load tuple space from file if exists
def load_tuple_space():
    global tuple_space
    if os.path.exists(tuple_space_file):
        with open(tuple_space_file, 'r') as file:
            tuple_space = json.load(file)
        logging.info("Tuple space loaded from file.")
    else:
        logging.info("No tuple space file found. Starting with empty tuple space.")

# Save tuple space to file
def save_tuple_space():
    with open(tuple_space_file, 'w') as file:
        json.dump(tuple_space, file)
    logging.info("Tuple space saved to file.")

# Handle client connections
def handle_client(client_socket):
    global total_operations, total_puts, total_gets, total_reads, total_errors

    try:
        # Set socket timeout
        client_socket.settimeout(10)

        # Receive request
        request = client_socket.recv(1024).decode('utf-8')
        logging.info(f"Received request: {request}")
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

    except socket.timeout:
        logging.error(f"Timeout occurred while handling client.")
        client_socket.send("024 ERR Timeout".encode('utf-8'))
    except Exception as e:
        logging.error(f"Error: {e}")
        client_socket.send("024 ERR Internal server error".encode('utf-8'))
    finally:
        save_tuple_space()
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

            logging.info(f"\nServer Statistics: "
                         f"Tuples: {num_tuples}, "
                         f"Avg Tuple Size: {avg_tuple_size:.2f}, "
                         f"Avg Key Size: {avg_key_size:.2f}, "
                         f"Avg Value Size: {avg_value_size:.2f}, "
                         f"Total Clients: {total_clients}, "
                         f"Total Operations: {total_operations}, "
                         f"Total READs: {total_reads}, "
                         f"Total GETs: {total_gets}, "
                         f"Total PUTs: {total_puts}, "
                         f"Total ERRs: {total_errors}")

# Server setup
def start_server(host, port):
    load_tuple_space()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Server started on {host}:{port}")

    # Start the statistics thread
    stats_thread = threading.Thread(target=print_statistics)
    stats_thread.daemon = True
    stats_thread.start()

    while True:
        client_socket, addr = server.accept()
        logging.info(f"Connection from {addr}")
        global total_clients
        total_clients += 1
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Start server
if __name__ == "__main__":
    start_server('localhost', 51234)
