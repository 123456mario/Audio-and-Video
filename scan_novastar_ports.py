import socket
import threading

TARGET_IP = "192.168.1.60"
# Novastar common ports: 5000 (LCT/SmartLCT), 5200 (Screen Control), 6666 (Monitor)
PORTS = [5000, 5001, 5200, 5201, 6000, 6666, 8080, 80]
SCAN_RANGE = range(4990, 6700) # Deep scan

print(f"🔎 Deep Scanning {TARGET_IP}...")

from concurrent.futures import ThreadPoolExecutor

def scan_tcp(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((TARGET_IP, port))
        if result == 0:
            print(f"✅ TCP Port {port} OPEN")
        s.close()
    except:
        pass

# Fast check common ports first
print("\n--- Checking Common Ports ---")
with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(scan_tcp, PORTS)

print("\n--- Deep Scanning Range (4990-6700) ---")
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_tcp, SCAN_RANGE)

print("\n--- Done ---")
