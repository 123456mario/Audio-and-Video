import socket
import sys

# Configuration: Target the Raspberry Pi
TARGET_IP = "192.168.1.50" 
PORT = 10008
CMD_STR = "BRI_100"

def send_udp():
    print(f"🚀 Sending UDP Command '{CMD_STR}' to {TARGET_IP}:{PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(CMD_STR.encode('utf-8'), (TARGET_IP, PORT))
        print("✅ UDP Packet Sent!")
        s.close()
    except Exception as e:
        print(f"❌ UDP Error: {e}")

if __name__ == "__main__":
    send_udp()
