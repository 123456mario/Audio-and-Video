import socket
import time

HOST = "127.0.0.1"
PORT = 1500

try:
    print(f"Connecting to Bridge at {HOST}:{PORT}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    # Test 1: Mute CH 5
    print("Sending: SET 5CHM TRUE (Mute)")
    s.sendall(b"SET 5CHM TRUE\r")
    time.sleep(1)
    
    # Test 2: Unmute CH 5
    print("Sending: SET 5CHM FALSE (Unmute)")
    s.sendall(b"SET 5CHM FALSE\r")
    time.sleep(1)
    
    # Test 3: Set Volume CH 5 to -10dB
    print("Sending: SET 5CHV -10.0 (Volume -10dB)")
    s.sendall(b"SET 5CHV -10.0\r")
    
    s.close()
    print("Done.")
    
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Is wing_to_xilica_simple.py running?")
