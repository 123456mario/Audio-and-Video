import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running (Remote): {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > 10: break
                data = os.read(fd, 1024)
                if not data: break
                output += data
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
            except OSError:
                break
        try: os.waitpid(pid, 0)
        except: pass
        return output.decode('utf-8', errors='ignore')

def diagnose():
    print("--- Checking Port 10025 ---")
    log = run_ssh_cmd(f"ssh {USER}@{HOST} 'netstat -tulpn | grep 10025'")
    print(log)
    print("--- Checking Running Python Processes ---")
    log2 = run_ssh_cmd(f"ssh {USER}@{HOST} 'ps aux | grep python'")
    print(log2)

if __name__ == "__main__":
    diagnose()
