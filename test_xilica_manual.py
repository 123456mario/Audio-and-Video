
import socket
import time

TARGET_IP = "192.168.1.50"
TARGET_PORT = 10024

def test_send():
    print(f"Connecting to {TARGET_IP}:{TARGET_PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        s.connect((TARGET_IP, TARGET_PORT))
        print("✅ Connected!")
        
        cmds = [
            "set 1chv 5.0",
            "set 1chv 8.0",
            "set 1chm TRUE",
            "set 1chm FALSE"
        ]
        
        for cmd in cmds:
            print(f"📤 Sending: {cmd}")
            s.send((cmd + "\r").encode())
            time.sleep(1)
            
        s.close()
        print("Done.")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_send()
