import socket
import time
import sys

CAM_IP = "192.168.1.31"  # Testing CAM2
UDP_PORT = 1259

def send_udp(cmd):
    # Panasonic UDP format: 02h + ASCII Command + 03h
    msg = b'\x02' + cmd.encode('ascii') + b'\x03'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending: {cmd} to {CAM_IP}:{UDP_PORT}")
    sock.sendto(msg, (CAM_IP, UDP_PORT))
    
    # Optional: Listen for ACK
    sock.settimeout(1.0)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"Received ACK: {data.hex()}")
    except socket.timeout:
        print("No response (Typical for UDP)")

if __name__ == "__main__":
    print("--- Testing Direct UDP (Port 1259) ---")
    send_udp("#PTS7550")  # Move Right
    time.sleep(1)
    send_udp("#PTS5050")  # Stop
    print("Done.")
