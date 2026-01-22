import socket
import time
import sys

BRIDGE_IP = "192.168.1.50"
BRIDGE_PORT = 10012

def send_cmd(universe, value):
    msg = bytes([universe, value])
    print(f"Sending Universe {universe}, Value {value} -> {msg.hex()}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(msg, (BRIDGE_IP, BRIDGE_PORT))

def main():
    print("Testing Art-Net Bridge...")
    
    # Test 1: Universe 0, Value 255 (Max)
    send_cmd(0, 255)
    time.sleep(0.5)
    
    # Test 2: Universe 1, Value 128 (Half)
    send_cmd(1, 128)
    time.sleep(0.5)
    
    # Test 3: Universe 0, Value 0 (Off)
    send_cmd(0, 0)
    
    print("Commands sent. Check bridge logs.")

if __name__ == "__main__":
    main()
