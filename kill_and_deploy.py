import pty
import os
import sys
import time
import re

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

def deploy():
    print("--- Aggressive Kill & Deploy ---")

    # 1. Find PID on Port 10025 and Kill it
    # Using lsof or netstat if available.
    # Fallback to pkill -f python
    kill_cmd = "fuser -k -n tcp 10025 || lsof -ti:10025 | xargs kill -9 || pkill -f bridge_v46.py || pkill -f osc_bridge_final.py"
    
    run_ssh_cmd(f"ssh {USER}@{HOST} '{kill_cmd}'")
    
    # 2. Wait a moment
    time.sleep(2)
    
    # 3. Transfer file again just to be sure
    local_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/bridge_v46.py"
    run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
    
    # 4. Start New Instance
    print("--- Launching bridge_v46.py ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u bridge_v46.py > bridge_log.txt 2>&1 &'")
    
    print("DONE. Checking logs in 3s...")
    time.sleep(3)
    
    log = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 10 ~/behringer-mixer/bridge_log.txt'")
    print(log)

if __name__ == "__main__":
    deploy()
