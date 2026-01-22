import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Executing: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- DIAGNOSING PORT 10025 ---")
    
    # Check who is using port 10025
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo lsof -i :10025'")
    
    print("--- KILLING EVERYTHING ON PORT 10025 ---")
    # Kill process using port 10025 directly
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo fuser -k 10025/tcp'")
    
    time.sleep(2)
    
    # Restart
    print("--- RESTARTING BRIDGE ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u final_wing_bridge_v5_debug.py > bridge_v5_log.txt 2>&1 &'")
