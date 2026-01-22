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

def manual_debug():
    print("--- 1. STOPPING SERVICE ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S systemctl stop osc_bridge'")
    
    print("\n--- 2. KILLING ZOMBIES ---")
    # Run twice to be sure
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S pkill -9 -f osc_bridge.py'")
    time.sleep(1)
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S pkill -9 -f osc_bridge.py'")
    
    print("\n--- 3. VERIFYING CLEAN STATE ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'ps aux | grep osc_bridge.py | grep -v grep'")
    
    print("\n--- 4. RUNNING MANUALLY (Press Ctrl+C to stop) ---")
    # Run directly in foreground to see startup logs instantly
    run_ssh_cmd(f"ssh {USER}@{HOST} 'python3 -u ~/behringer-mixer/osc_bridge.py'")

if __name__ == "__main__":
    manual_debug()
