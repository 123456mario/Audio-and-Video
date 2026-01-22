import socket

TCP_IP = "0.0.0.0"
TCP_PORT = 10007

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(1)

print(f"Xilica Mock Server listening on {TCP_PORT}...")

while True:
    conn, addr = sock.accept()
    data = conn.recv(1024)
    if data:
        print(f"Xilica Received: {data.decode().strip()}")
    conn.close()
