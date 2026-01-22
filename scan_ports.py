import socket
import threading
from queue import Queue

target_ip = "192.168.1.60"
ports_to_scan = [5000, 5001, 5200, 5201, 6000, 6666, 80, 8080]

print(f"🔎 Scanning {target_ip} for open ports...")

def scan_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target_ip, port))
        if result == 0:
            print(f"✅ Port {port} is OPEN!")
        s.close()
    except:
        pass

threads = []
for port in ports_to_scan:
    t = threading.Thread(target=scan_port, args=(port,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("🏁 Scan complete.")
