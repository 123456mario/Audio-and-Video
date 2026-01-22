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

def deploy_sniffer():
    print("--- DEPLOYING SNIFFER ---")
    
    # 1. Kill old bridge
    run_ssh_cmd(f"ssh {USER}@{HOST} 'sudo fuser -k -9 10025/tcp; pkill -f python'")
    time.sleep(1)
    
    # 2. Transfer Sniffer
    local_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/sniffer_debug_master.py"
    run_ssh_cmd(f"scp {local_path} {USER}@{HOST}:~/behringer-mixer/")
    
    # 3. Running Interactively? No, creating log
    print("--- RUNNING SNIFFER (Background) ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u sniffer_debug_master.py > sniffer_log.txt 2>&1 &'")
    
    print("DONE. Ready to spy on Xilica.")

if __name__ == "__main__":
    deploy_sniffer()
