import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Executing: {cmd}")
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
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print(f"--- Deploying Service to Pi ({HOST}) ---")
    
    print("\n1. Installing Service File & Script:")
    run_ssh_cmd(f"scp osc_bridge.py {USER}@{HOST}:~/behringer-mixer/")
    run_ssh_cmd(f"scp discover_wing.py {USER}@{HOST}:~/behringer-mixer/")
    run_ssh_cmd(f"scp behringer_wing.service {USER}@{HOST}:~/")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo mv ~/behringer_wing.service /etc/systemd/system/'")
    
    # 2. Reload and Enable
    print("\n2. Enabling Service:")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo systemctl daemon-reload'")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo systemctl enable behringer_wing'")
    
    # 3. Restart and Check
    print("\n3. Starting Service:")
    # Stop existing instance first
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo pkill -f osc_bridge.py || true'")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo systemctl restart behringer_wing'")
    
    print("\n4. Checking Status:")
    time.sleep(2)
    status = run_ssh_cmd(f"ssh {USER}@{HOST} 'systemctl status behringer_wing'")
    print(status)
