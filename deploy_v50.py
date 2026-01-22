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

def deploy_v50():
    print("--- DEPLOYING BRIDGE V5.0 (FINAL ROBUST) ---")
    
    # 1. Kill old
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f python || true'")
    time.sleep(1)
    
    # 2. Transfer
    local_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/bridge_v50.py"
    run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
    
    # 3. Running
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u bridge_v50.py > bridge_log.txt 2>&1 &'")
    
    print("DONE. Monitoring Logs...")
    time.sleep(3)
    log = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 15 ~/behringer-mixer/bridge_log.txt'")
    print(log)

if __name__ == "__main__":
    deploy_v50()
