import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

# Files to transfer
FILES = ["final_wing_bridge_v5_debug.py"]

def run_ssh_cmd(cmd):
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        # Child
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        # Parent
        output = b""
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                # Monitor output
                sys.stdout.buffer.write(data)
                sys.stdout.flush()

                # Automated password handling
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
    print("--- Starting Automated Bridge V5 Deployment ---")
    
    # 1. Create target directory
    run_ssh_cmd(f"ssh {USER}@{HOST} 'mkdir -p ~/behringer-mixer'")
    
    # 2. Transfer the script
    for f in FILES:
        local_path = f"/Users/gimdongseong/Documents/GitHub/behringer-mixer/{f}"
        if os.path.exists(local_path):
            print(f"--- Transferring {f} ---")
            run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
        else:
            print(f"--- FAILED: {f} not found locally! ---")

    # 3. Kill existing process
    print("--- Cleaning up old instances ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f final_wing_bridge_v5_debug.py || true'")

    # 4. Run the script on Pi
    print("--- Launching Bridge V5 on Pi ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u final_wing_bridge_v5_debug.py > bridge_v5_log.txt 2>&1 &'")
    
    print("\n--- Deployment Complete! ---")
    print(f"Bridge is running on Pi at {HOST}")
    print("Logs: ~/behringer-mixer/bridge_v5_log.txt")

if __name__ == "__main__":
    deploy()
