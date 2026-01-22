import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

# Script to deploy
LOCAL_FILE = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/wing_to_xilica_final.py"
# MATCHING THE PATH FROM THE LOGS: /home/pi/behringer-mixer/osc_bridge.py
REMOTE_DIR = "behringer-mixer" 
REMOTE_FILE = "osc_bridge.py"

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
                
                # Monitor output
                sys.stdout.buffer.write(data)
                sys.stdout.flush()

                # Password handling
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

def deploy():
    print("--- Starting Wing Bridge Deployment (Fixing Port Conflict) ---")
    
    # 1. Kill existing zombie process FIRST
    print("--- Killing lingering osc_bridge processes ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f osc_bridge.py || true'")
    # Explicitly killing PID 944 seen in logs if pkill fails, but pkill -f should get it
    time.sleep(2)

    # 2. Transfer file
    if os.path.exists(LOCAL_FILE):
        print(f"--- Transferring to ~/{REMOTE_DIR}/{REMOTE_FILE} ---")
        # Ensure dir exists
        run_ssh_cmd(f"ssh {USER}@{HOST} 'mkdir -p ~/{REMOTE_DIR}'")
        run_ssh_cmd(f"scp {LOCAL_FILE} {USER}@{HOST}:~/{REMOTE_DIR}/{REMOTE_FILE}")
    else:
        print(f"ERROR: Local file not found: {LOCAL_FILE}")
        return

    # 3. Restart Service
    print("--- Restarting osc_bridge.service ---")
    # Using sudo -S to pipe password
    cmd = f"echo {PASS} | sudo -S systemctl restart osc_bridge"
    run_ssh_cmd(f"ssh {USER}@{HOST} '{cmd}'")
    
    print("\n--- Deployment Complete ---")
    print("Service restarted and old processes killed.")

if __name__ == "__main__":
    deploy()
