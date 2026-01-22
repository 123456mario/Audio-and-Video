import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running: {cmd}")
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
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

def fix():
    print("--- Terminating Stuck Processes ---")
    
    # 1. Stop Systemd Service
    print("Stopping osc_bridge.service...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S systemctl stop osc_bridge'")
    time.sleep(2)
    
    # 2. Force Kill Specific Process Pattern
    print("Sending SIGKILL to any osc_bridge.py...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S pkill -9 -f osc_bridge.py'")
    time.sleep(2)
    
    # 3. Verify Clean
    print("Checking for survivors...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'ps aux | grep osc_bridge.py | grep -v grep'")
    
    # 4. Start Service
    print("--- Starting Service ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S systemctl start osc_bridge'")
    time.sleep(2)
    
    # 5. Check Log
    print("--- Checking Status ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'systemctl status osc_bridge'")

if __name__ == "__main__":
    fix()
