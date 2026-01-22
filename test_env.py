import socket
import os
import subprocess
import time

def check_port(port):
    print(f"[*] Checking Port {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.bind(("0.0.0.0", port))
        print(f"    ✅ Port {port} is FREE. Ready to bind.")
        sock.close()
        return True
    except OSError:
        print(f"    ❌ Port {port} is BUSY (Address already in use).")
        # Find who is using it
        try:
            res = subprocess.check_output(f"sudo lsof -i :{port} -t", shell=True).decode().strip()
            print(f"    ⚠️ Process PID holding port: {res}")
            return int(res)
        except:
            print("    ⚠️ Could not identify PID (permission denied?)")
            return None

def check_ping(ip):
    print(f"[*] Pinging {ip}...")
    try:
        ret = os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1")
        if ret == 0:
            print(f"    ✅ {ip} is ALIVE.")
        else:
            print(f"    ❌ {ip} is UNREACHABLE.")
    except:
        print("    ⚠️ Ping failed.")

print("=== 🛠️ Raspberry Pi Environment Diagnostic 🛠️ ===")
print("1. Checking Xilica Server Port (10001)")
pid = check_port(10001)

if pid:
    print(f"\n2. Attempting to KILL blocking process {pid}...")
    os.system(f"sudo kill -9 {pid}")
    time.sleep(1)
    check_port(10001)

print("\n3. Network Connectivity Check")
check_ping("192.168.1.11") # Wing
check_ping("192.168.1.20") # Xilica

print("\n=== ✨ Done. Try running osc_bridge.py now. ===")
