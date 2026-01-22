import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

LOCAL_FILE = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/scan_wing_ports.py"
REMOTE_FILE = "scan_wing_ports.py"

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

def run_scan():
    print("--- Deploying Port Scanner ---")
    
    # 1. Stop service to free network logic
    print("Stopping osc_bridge...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S systemctl stop osc_bridge'")
    
    # 2. Transfer
    if os.path.exists(LOCAL_FILE):
        run_ssh_cmd(f"scp {LOCAL_FILE} {USER}@{HOST}:~/{REMOTE_FILE}")
    
    # 3. Run
    print("\n--- executing Scanner ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'python3 -u ~/{REMOTE_FILE}'")
    
    # 4. Restart service
    print("\n--- Restoring Service ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S systemctl start osc_bridge'")

if __name__ == "__main__":
    run_scan()
