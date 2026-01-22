import socket
import threading
from queue import Queue

target_port = 5200
subnet_base = "192.168.1."
timeout = 0.5

print(f"🔎 Scanning subnet {subnet_base}x for Port {target_port} (Novastar)...")

def scan_ip(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, target_port))
        if result == 0:
            print(f"✅ FOUND! {ip} is listening on Port {target_port}")
        s.close()
    except:
        pass

threads = []
for i in range(1, 255):
    ip = f"{subnet_base}{i}"
    t = threading.Thread(target=scan_ip, args=(ip,))
    threads.append(t)
    t.start()
    # Limit thread batches to avoid OS limit
    if i % 50 == 0:
        for t_join in threads: t_join.join()
        threads = []

for t in threads:
    t.join()

print("🏁 Subnet Scan complete.")
