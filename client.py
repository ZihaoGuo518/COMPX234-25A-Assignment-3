import socket
import time
import logging

# Setup logging
logging.basicConfig(filename='client.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Client settings
SERVER_HOST = 'localhost'
SERVER_PORT = 51234
RETRIES = 3
TIMEOUT = 10  # seconds

# Send request to the server
def send_request(command, key, value=None):
    attempt = 0
    while attempt < RETRIES:
        try:
            # Create the socket and connect
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(TIMEOUT)
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            # Prepare the request message
            if command == 'P':  # PUT
                request_message = f"PUT {key} {value}"
            elif command == 'R':  # READ
                request_message = f"READ {key}"
            elif command == 'G':  # GET
                request_message = f"GET {key}"
            else:
                logging.error("Invalid command")
                return

            # Send the request
            client_socket.send(request_message.encode('utf-8'))
            logging.info(f"Sent request: {request_message}")

            # Receive the server response
            response = client_socket.recv(1024).decode('utf-8')
            logging.info(f"Received response: {response}")

            # Check for acknowledgment
            if response.startswith("018 OK"):
                logging.info(f"Request successful: {response}")
            else:
                logging.error(f"Error in request: {response}")

            # Close socket and break on success
            client_socket.close()
            return response

        except socket.timeout:
            logging.error(f"Request timeout on attempt {attempt + 1}")
            attempt += 1
        except Exception as e:
            logging.error(f"Error: {e}")
            attempt += 1
        finally:
            if attempt == RETRIES:
                logging.error("Max retries reached, request failed.")
                return "024 ERR Max retries reached"

# Example usage of the client for various operations
if __name__ == "__main__":
    # PUT request
    response = send_request('P', 'key1', 'value1')
    print(f"Response: {response}")

    # READ request
    response = send_request('R', 'key1')
    print(f"Response: {response}")

    # GET request
    response = send_request('G', 'key1')
    print(f"Response: {response}")

    # Invalid command (example)
    response = send_request('X', 'key1')
    print(f"Response: {response}")
