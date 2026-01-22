import pty
import os
import sys
import time

# Raspberry Pi Credentials (found in deploy_to_pi.py)
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

# Files to transfer
FILES = ["ptz_cam.py"]

def run_ssh_cmd(cmd, interaction=True):
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
                
                # Monitor output to provide basic visual feedback
                sys.stdout.buffer.write(data)
                sys.stdout.flush()

                # Automated password/confirmation handling
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
    print("--- Starting Automated PTZ Deployment ---")
    
    # 1. Create target directory
    run_ssh_cmd(f"ssh {USER}@{HOST} 'mkdir -p ~/behringer-mixer'")
    
    # 2. Transfer the ptz_cam.py script
    for f in FILES:
        local_path = f"/Users/gimdongseong/Documents/GitHub/behringer-mixer/{f}"
        if os.path.exists(local_path):
            print(f"--- Transferring {f} ---")
            run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
        else:
            print(f"--- FAILED: {f} not found locally! ---")

    # 3. Kill existing process if any
    print("--- Cleaning up old instances ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f ptz_cam.py || true'")

    # 4. Run the script on Pi
    print("--- Launching PTZ Control on Pi (Unbuffered) ---")
    # Using python3 -u to ensure logs are written to file immediately
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u ptz_cam.py > ptz_log.txt 2>&1 &'")
    
    print("\n--- Deployment Complete! ---")
    print(f"Server is now running on Pi at {HOST}:10001 (UDP)")
    print("Check ~/behringer-mixer/ptz_log.txt on Pi for logs.")

if __name__ == "__main__":
    deploy()
