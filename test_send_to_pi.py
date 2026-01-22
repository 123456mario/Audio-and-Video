import socket
import time

UDP_IP = "192.168.1.50"
UDP_PORT = 10021
MESSAGE = b"\x00\xFF" # Universe 0, Value 255

print(f"Sending test packet to {UDP_IP}:{UDP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    print("Packet sent successfully.")
except Exception as e:
    print(f"Error sending packet: {e}")
finally:
    sock.close()
