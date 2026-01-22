import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
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
    print(f"--- Checking Live Traffic on Pi ({HOST}) ---")
    
    # Check if process is running
    pid = run_ssh_cmd(f"ssh {USER}@{HOST} 'pgrep -f artnet_bridge.py'").strip()
    if not pid or not pid.isdigit():
        print("WARNING: artnet_bridge.py is NOT running!")
    else:
        print(f"Process OK (PID {pid}). Reading Log...")
        # Read the last 50 lines of the debug log
        log_out = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 50 /home/pi/behringer-mixer/debug_bridge.log'")
        print(log_out)
