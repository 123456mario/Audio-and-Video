import socket
import sys

TARGET_IP = "192.168.1.60"
PORTS = [5200, 15200, 6666]
# Standard Read Mode (Heartbeat)
CMD = bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56")

print(f"📡 Checking UDP on {TARGET_IP}...")

for port in PORTS:
    print(f"   Probing UDP Port {port}...", end='', flush=True)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3.0)
        s.sendto(CMD, (TARGET_IP, port))
        data, _ = s.recvfrom(1024)
        print(f"  ✅ YES! Response: {data.hex()}")
    except socket.timeout:
        print("  ❌ No response")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
    finally:
        s.close()
