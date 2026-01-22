import pty
import os
import sys
import time

# Connection details (From deploy_to_pi.py)
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

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
                
                # Check for password prompt
                if b"password:" in data.lower():
                    os.write(fd, f"{PASS}\n".encode())
                
                # Check for "Are you sure..." (Host key fingerprint)
                if b"continue connecting" in data.lower():
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

def main():
    print("=== Deploying Art-Net Bridge to Raspberry Pi ===")
    
    # 1. Create Directory (Just in case)
    print("--- 1. Checking Directory ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'mkdir -p ~/behringer-mixer'")
    
    # 2. Transfer Script
    print("--- 2. Transferring artnet_bridge.py ---")
    # Assuming the script runs from the project root
    cwd = os.getcwd()
    src_path = os.path.join(cwd, "artnet_bridge.py")
    
    if not os.path.exists(src_path):
        print(f"Error: Could not find {src_path}")
        return

    cmd_scp = f"scp {src_path} {USER}@{HOST}:~/behringer-mixer/"
    print(run_ssh_cmd(cmd_scp))
    
    # 3. Kill existing instance (if any)
    print("--- 3. Stopping any existing instances ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f artnet_bridge.py'")
    
    # 4. Run in Background
    print("--- 4. Starting Bridge on Pi ---")
    # Use nohup to keep it running after disconnect
    # We use python3 directly (standard libs only)
    cmd_run = f"ssh {USER}@{HOST} 'nohup python3 ~/behringer-mixer/artnet_bridge.py > ~/behringer-mixer/artnet_log.txt 2>&1 &'"
    print(run_ssh_cmd(cmd_run))
    
    print("=== Deployment Complete ===")
    print("Bridge should be running on Port 10012")

if __name__ == "__main__":
    main()
