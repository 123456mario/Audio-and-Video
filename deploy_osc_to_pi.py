import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"
FILE = "osc_bridge.py"
REMOTE_PATH = "/home/pi/behringer-mixer/osc_bridge.py"

def run_interaction(cmd):
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        while time.time() - start_time < 30: # 30s timeout
            try:
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                # Echo to console (optional)
                # sys.stdout.write(data.decode('utf-8', errors='ignore'))
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        try:
            _, status = os.waitpid(pid, 0)
        except:
            pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- DEPLOYING OSC BRIDGE TO PI ---")
    
    # 1. SCP
    print(f"Uploading {FILE}...")
    run_interaction(f"scp {FILE} {USER}@{HOST}:{REMOTE_PATH}")
    
    # 2. Restart Service
    print("Restarting osc_bridge.py...")
    # Kill existing
    run_interaction(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S pkill -f osc_bridge.py'")
    # Allow time to die
    time.sleep(2)
    # Start new (nohup)
    run_interaction(f"ssh {USER}@{HOST} 'nohup python3 -u {REMOTE_PATH} > /home/pi/behringer-mixer/osc.log 2>&1 &'")
    
    print("--- OSC DEPLOYMENT COMPLETE ---")
