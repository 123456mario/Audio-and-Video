import socket

TARGET_IP = "192.168.1.60"
PORT = 15200

# Pro Series Heartbeat Command (Read Mode)
# 55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56
CMD_HEX = "55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56"
CMD_BYTES = bytes.fromhex(CMD_HEX.replace(" ", ""))

print(f"📡 Sending UDP Heartbeat to {TARGET_IP}:{PORT}...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3.0)

try:
    sock.sendto(CMD_BYTES, (TARGET_IP, PORT))
    print("✅ Packet sent. Waiting for response...")
    data, addr = sock.recvfrom(1024)
    print(f"📥 Received UDP Response from {addr}: {data.hex()}")
except socket.timeout:
    print("❌ No UDP response received (Timeout)")
except Exception as e:
    print(f"⚠️ Error: {e}")
finally:
    sock.close()
