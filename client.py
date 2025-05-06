import socket
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])
REQ_FILE = sys.argv[3]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    with open(REQ_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            message = f"{len(line)+4:03} {line}"  # Add size prefix
            s.sendall(message.encode())
            response = s.recv(1024).decode()
            print(f"{line}: {response}")
