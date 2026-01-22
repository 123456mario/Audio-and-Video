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

def force_restart():
    print("--- FORCE KILLING & RESTARTING BRIDGE ---")
    
    # 1. Aggressive Kill (Port 10025 + Python Name)
    # Using fuser to kill specific port holder, then pkill for good measure
    cmd_kill = "sudo fuser -k -9 10025/tcp; sudo pkill -9 -f python; sudo pkill -9 -f bridge"
    run_ssh_cmd(f"ssh {USER}@{HOST} '{cmd_kill}'")
    time.sleep(3) # Wait for kernel to release port
    
    # 2. Restart Existing Safe File
    print("--- STARTING BRIDGE... ---")
    cmd_run = "cd ~/behringer-mixer && nohup python3 -u final_wing_bridge_v5_safe.py > bridge_safe_log.txt 2>&1 &"
    run_ssh_cmd(f"ssh {USER}@{HOST} '{cmd_run}'")
    
    print("DONE. Checking Logs for Success...")
    time.sleep(3)
    log = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 20 ~/behringer-mixer/bridge_safe_log.txt'")
    print(log)

if __name__ == "__main__":
    force_restart()
