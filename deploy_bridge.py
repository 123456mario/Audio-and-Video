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
FILES = ["osc_bridge_final.py"]

def run_ssh_cmd(cmd, interaction=True):
    print(f"Running (Remote): {cmd}")
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
        
        try:
            _, status = os.waitpid(pid, 0)
        except ChildProcessError:
            pass
        return output.decode('utf-8', errors='ignore')

def deploy():
    print("--- Starting OSC Bridge Deployment (Offline/Robust) ---")
    
    # 1. Create target directories
    run_ssh_cmd(f"ssh {USER}@{HOST} 'mkdir -p ~/behringer-mixer/deps'")
    
    # 2. Transfer Dependencies (python-osc wheel)
    deps = glob.glob("deps/*.whl")
    if deps:
        for dep in deps:
            print(f"--- Transferring dependency: {dep} ---")
            # We assume dep path is relative to current directory
            local_dep_path = os.path.abspath(dep)
            run_ssh_cmd(f"scp {local_dep_path} {USER}@{HOST}:~/behringer-mixer/deps/")
            
        # 3. Install Dependencies on Pi
        print("--- Installing Dependencies on Pi ---")
        # Use --no-index --find-links to force using transferred files
        run_ssh_cmd(f"ssh {USER}@{HOST} 'pip3 install ~/behringer-mixer/deps/*.whl --break-system-packages --force-reinstall || pip3 install ~/behringer-mixer/deps/*.whl --force-reinstall'")
    else:
        print("⚠️ No dependencies found in ./deps. Skipping offline install.")

    # 4. Transfer the osc_bridge_final.py script
    for f in FILES:
        local_path = f"/Users/gimdongseong/Documents/GitHub/behringer-mixer/{f}"
        if os.path.exists(local_path):
            print(f"--- Transferring {f} ---")
            run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
        else:
            print(f"--- FAILED: {f} not found locally! ---")
            return

    # 5. Kill existing process if any
    print("--- Cleaning up old instances ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f osc_bridge_final.py || true'")

    # 6. Run the script on Pi
    print("--- Launching OSC Bridge on Pi (Unbuffered) ---")
    # Using python3 -u to ensure logs are written to file immediately
    # We log to bridge_log.txt for debugging
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u osc_bridge_final.py > bridge_log.txt 2>&1 &'")
    
    print("\n--- Deployment Complete! ---")
    print(f"Bridge is now running on Pi at {HOST}")
    print("Check ~/behringer-mixer/bridge_log.txt on Pi for logs.")

if __name__ == "__main__":
    deploy()
