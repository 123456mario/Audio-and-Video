import socket

# Listen on ALL interfaces on port 1500 (UDP)
UDP_IP = "0.0.0.0"
UDP_PORT = 1500

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind((UDP_IP, UDP_PORT))
    print(f"=== UDP SNIFFER LISTENING ON PORT {UDP_PORT} ===")
    print("Waiting for ANY data from Xilica...")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"received message: {data} from {addr}")
        print(f"Hex: {data.hex()}")
except OSError as e:
    print(f"Error binding to port {UDP_PORT}: {e}")
