# 1. IP가 고정된 파일 생성

import socket
import sys
import time

# 대상 IP (여기에 고정했습니다)
TARGET_IP = "192.168.1.60"
PORT = 5200

# Hex Command: Set Brightness to 100% (FF)
CMD_HEX = "55 aa 00 00 fe 00 00 00 00 00 00 00 04 00 00 00 01 00 ff ca 56"
CMD_BYTES = bytes.fromhex(CMD_HEX.replace(" ", ""))

def send_cmd():
    print(f"🚀 Sending Brightness Command to {TARGET_IP}:{PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((TARGET_IP, PORT))
        s.send(CMD_BYTES)
        print("✅ Command Sent!")
        try:
            resp = s.recv(1024)
            print(f"📥 Response: {resp.hex()}")
        except socket.timeout:
            print("⚠️ No response (Normal for some Novastar commands)")
        s.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_cmd()


# 2. 실행 (이제 IP 입력 안 하셔도 됩니다)
