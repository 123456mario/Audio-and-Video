import socket
import threading
from queue import Queue

target_ip = "192.168.1.60"
print(f"🔎 Full Port Scan on Unico ({target_ip})...")

def scan_worker(port_q):
    while True:
        port = port_q.get()
        if port is None: break
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((target_ip, port)) == 0:
                print(f"✅ OPEN PORT: {port}")
            s.close()
        except: pass
        port_q.task_done()

q = Queue()
threads = []
for _ in range(50): # 50 threads
    t = threading.Thread(target=scan_worker, args=(q,))
    t.start()
    threads.append(t)

# Prioritize likely ports first
common = [5000, 5200, 80, 8080, 19999, 23, 22, 9000, 4001, 8888]
for p in common: q.put(p)

# Then scan range 1000-10000 (likely range for custom controls)
for p in range(1000, 10001):
    if p not in common: q.put(p)

q.join()

# Stop threads
for _ in range(50): q.put(None)
for t in threads: t.join()

print("🏁 Scan complete.")
