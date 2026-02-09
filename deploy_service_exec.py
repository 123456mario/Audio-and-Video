import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running (Remote): {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > 15: break
                data = os.read(fd, 1024)
                if not data: break
                output += data
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
            except OSError:
                break
        try: os.waitpid(pid, 0)
        except: pass
        return output.decode('utf-8', errors='ignore')

def deploy_service():
    print("--- DEPLOYING SYSTEMD SERVICE ---")
    
    # 1. Kill old processes using port 10025
    print("Cleaning up port 10025...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo fuser -k -9 10025/tcp || true'")
    time.sleep(1)
    
    # 2. Transfer service file
    local_service_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/wing_bridge.service"
    print(f"Transferring {local_service_path}...")
    run_ssh_cmd(f"scp {local_service_path} {USER}@{HOST}:~/behringer-mixer/wing_bridge.service")
    
    # 3. Move to /etc/systemd/system and reload
    print("Installing and enabling service...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo mv ~/behringer-mixer/wing_bridge.service /etc/systemd/system/wing_bridge.service'")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo systemctl daemon-reload'")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo systemctl enable wing_bridge.service'")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo systemctl restart wing_bridge.service'")
    
    print("DONE. Checking status...")
    time.sleep(2)
    status = run_ssh_cmd(f"ssh {USER}@{HOST} 'systemctl status wing_bridge.service --no-pager'")
    print("-" * 30)
    print(status)
    print("-" * 30)

if __name__ == "__main__":
    deploy_service()
