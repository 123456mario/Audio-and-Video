import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running (Remote): {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        # Child
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        # Parent
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
        
        try:
           os.waitpid(pid, 0)
        except: pass
        return output.decode('utf-8', errors='ignore')

def fetch():
    print("--- Fetching Bridge Logs ---")
    log = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 20 ~/behringer-mixer/bridge_log.txt'")
    print("\n--- LOG OUTPUT START ---")
    print(log)
    print("--- LOG OUTPUT END ---")

if __name__ == "__main__":
    fetch()
