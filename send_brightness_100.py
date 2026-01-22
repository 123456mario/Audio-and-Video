import socket
import time

# Configuration
NOVASTAR_IP = "192.168.1.60"
NOVASTAR_PORT = 15200

# Pro Series Checksum Logic
def calc_cmd(payload_hex):
    payload = bytes.fromhex(payload_hex.replace(" ", ""))
    checksum = sum(payload) + 0x5555
    sum_l = checksum & 0xFF
    sum_h = (checksum >> 8) & 0xFF
    # Header 55 aa + payload + checksum little endian
    return b'\x55\xaa' + payload + bytes([sum_l, sum_h])

# Command Definition
BRI_HEADER = "00 00 fe ff 01 ff ff ff 01 00 01 00 00 02 01 00"
# 100% Brightness is FF
CMD_BRI_100 = calc_cmd(BRI_HEADER + " ff")

def send_to_novastar_direct(cmd_bytes):
    print(f"Target: {NOVASTAR_IP}:{NOVASTAR_PORT}")
    print(f"Sending Bytes: {cmd_bytes.hex()}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((NOVASTAR_IP, NOVASTAR_PORT))
        s.send(cmd_bytes)
        
        # Optional: Listen for Ack
        try:
            resp = s.recv(1024)
            print(f"Response: {resp.hex()}")
        except socket.timeout:
            print("No response received (typical for some commands)")
            
        s.close()
        print("✅ Sent Successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send: {e}")
        return False

if __name__ == "__main__":
    send_to_novastar_direct(CMD_BRI_100)
