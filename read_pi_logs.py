import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"
CMD = "cat /home/pi/behringer-mixer/artnet.log"

def run_ssh_cmd(cmd):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
            except OSError:
                break
        
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print(f"--- LOGS FROM PI ({HOST}) ---")
    logs = run_ssh_cmd(f"ssh {USER}@{HOST} '{CMD}'")
    print(logs)
