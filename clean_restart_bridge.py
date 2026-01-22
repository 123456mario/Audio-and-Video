import pty
import os
import sys
import time

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

def clean_deploy():
    print("--- Killing Old Processes ---")
    # Kill specific PIDs found earlier or generic pattern
    run_ssh_cmd(f"ssh {USER}@{HOST} 'kill -9 168005 168053 || pkill -f bridge_v46.py'")
    
    time.sleep(2)
    
    print("--- Starting Clean Instance ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'cd ~/behringer-mixer && nohup python3 -u bridge_v46.py > bridge_log.txt 2>&1 &'")
    
    print("DONE. Logs in 3s...")
    time.sleep(3)
    log = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 10 ~/behringer-mixer/bridge_log.txt'")
    print(log)

if __name__ == "__main__":
    clean_deploy()
