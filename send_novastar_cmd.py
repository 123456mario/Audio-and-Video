import socket
import sys
import time

# Hex Command: Pro Series Brightness 0% (Calculated with +0x5555 checksum)
# 55 aa 00 00 fe ff 01 ff ff ff 01 00 01 00 00 02 01 00 00 55 5a
CMD_HEX = "55 aa 00 00 fe ff 01 ff ff ff 01 00 01 00 00 02 01 00 00 55 5a"
CMD_BYTES = bytes.fromhex(CMD_HEX.replace(" ", ""))

def send_cmd(ip, port=15200):
    print(f"📉 Sending PRO SERIES Brightness 0% to {ip}:{port}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, port))
        s.send(CMD_BYTES)
        print("✅ Command Sent! Check screen.")
        
        # Optional: Read response
        try:
            resp = s.recv(1024)
            print(f"📥 Response: {resp.hex()}")
        except socket.timeout:
            print("⚠️ No response (Normal for some Novastar commands)")
            
        s.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 send_novastar_cmd.py <IP_ADDRESS>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    send_cmd(target_ip)
