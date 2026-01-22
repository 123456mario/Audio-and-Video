import pty
import os
import sys
import time
import glob

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

# Files to transfer
FILES = ["bridge_v46.py"]

def run_ssh_cmd(cmd, interaction=True):
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
                # Timeout safety
                if time.time() - start_time > 15:
                    break
                    
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
        
        try:
            _, status = os.waitpid(pid, 0)
        except ChildProcessError:
            pass
        return output.decode('utf-8', errors='ignore')

def deploy():
    print("--- Deploying Fixed bridge_v46.py to Pi ---")
    
    # 1. Transfer the bridge_v46.py script
    for f in FILES:
        local_path = f"/Users/gimdongseong/Documents/GitHub/behringer-mixer/{f}"
        if os.path.exists(local_path):
            print(f"--- Transferring {f} ---")
            run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
        else:
            print(f"--- FAILED: {f} not found locally! ---")
            return

    # 2. Kill existing process if any
    print("--- Cleaning up old instances ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f bridge_v46.py || true'")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f osc_bridge_final.py || true'")

    # 3. Run the script on Pi
    print("--- Launching bridge_v46.py on Pi ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u bridge_v46.py > bridge_log.txt 2>&1 &'")
    
    print("\n--- Deployment Complete! ---")

if __name__ == "__main__":
    deploy()
