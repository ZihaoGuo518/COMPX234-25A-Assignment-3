import socket
import sys

def send_request(host, port, request):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Send request to server
    client.send(request.encode('utf-8'))

    # Receive and print the response
    response = client.recv(1024).decode('utf-8')
    print(f"Server response: {response}")

    client.close()

# Read request file and send requests
def main():
    if len(sys.argv) != 4:
        print("Usage: client.py <hostname> <port> <request_file>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    request_file = sys.argv[3]

    with open(request_file, 'r') as file:
        for line in file:
            send_request(host, port, line.strip())

if __name__ == "__main__":
    main()
