import socket
import time

IP = "192.168.1.9"
PORT = 10001

commands = [
    "CAM1 LEFT ON",
    "CAM1 STOP ON",
    "CAM2 UP ON",
    "CAM2 HOME ON",
    "STOP" # Global Stop
]

print(f"🚀 PTZ Integration Test ({IP}:{PORT})")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT))
    
    for cmd in commands:
        full_cmd = f"{cmd}\r\n"
        print(f"👉 Sending: {full_cmd.strip()}")
        sock.send(full_cmd.encode())
        resp = sock.recv(1024)
        print(f"   Response: {resp.decode().strip()}")
        time.sleep(1.5)
        
    sock.close()
    print("✅ Test Complete.")

except Exception as e:
    print(f"❌ Error: {e}")
