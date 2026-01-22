import socket
import time

# IP of the Mac's network interface (en8)
TARGET_IP = "192.168.1.9" 
TCP_PORT = 10001

def send_test():
    print(f"Connecting to {TARGET_IP}:{TCP_PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((TARGET_IP, TCP_PORT))
        
        cmd = "set ch1vol -80.0\r\n"
        print(f"Sending: {cmd.strip()}")
        s.send(cmd.encode())
        
        resp = s.recv(1024)
        print(f"Received: {resp.decode().strip()}")
        
        s.close()
        print("✅ Connection Successful via External IP")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    send_test()
