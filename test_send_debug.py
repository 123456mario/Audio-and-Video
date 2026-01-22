import socket
import time

UDP_IP = "192.168.1.50"
PORTS = [10012, 10021]
MESSAGE = b"TEST_PACKET_FROM_LAPTOP"

print(f"--- SENDING TEST PACKETS TO {UDP_IP} ---")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    for port in PORTS:
        print(f"Sending to Port {port}...")
        sock.sendto(MESSAGE, (UDP_IP, port))
        time.sleep(0.1)
        sock.sendto(MESSAGE, (UDP_IP, port)) # Send twice
    print("Locked and loaded. Packets sent.")
except Exception as e:
    print(f"Error: {e}")
finally:
    sock.close()
