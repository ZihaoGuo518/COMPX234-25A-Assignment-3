import threading
import socket

def handle_client(conn, addr):
    print(f"Handling client {addr}")
    conn.close()

HOST = 'localhost'
PORT = 51234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

while True:
    conn, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
