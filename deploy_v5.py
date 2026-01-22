import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"
FILE = "final_wing_bridge_v5_debug.py"
REMOTE_PATH = "/home/pi/behringer-mixer/final_wing_bridge_v5_debug.py"
LOG_FILE = "/home/pi/behringer-mixer/bridge_v5.log"

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
                
                # Echo to console (Real-time feedback)
                sys.stdout.write(data.decode('utf-8', errors='ignore'))
                sys.stdout.flush()
                
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
    print("--- DEPLOYING V5 BRIDGE ---")
    
    # 0. Create remote directory if not exists (Safe measure)
    # run_interaction(f"ssh {USER}@{HOST} 'mkdir -p /home/pi/behringer-mixer'")

    # 1. SCP Upload
    print(f"Uploading {FILE}...")
    run_interaction(f"scp {FILE} {USER}@{HOST}:{REMOTE_PATH}")
    
    # 2. Kill Existing Bridge
    print("Stopping previous instances...")
    # Kill any python script running 'bridge' logic to be safe
    run_interaction(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S pkill -f final_wing_bridge'")
    time.sleep(1)
    
    # 3. Start V5 Bridge (Background)
    print(f"Starting {FILE}...")
    # Use -u for unbuffered output
    run_interaction(f"ssh {USER}@{HOST} 'nohup python3 -u {REMOTE_PATH} > {LOG_FILE} 2>&1 &'")
    
    print("--- BRIDGE STARTED ---")
    print("Tailing logs for verification (5 seconds)...")
    time.sleep(2)
    run_interaction(f"ssh {USER}@{HOST} 'tail -n 10 {LOG_FILE}'")
