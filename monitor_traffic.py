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
        # Child
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        # Parent
        output = b""
        start_time = time.time()
        while True:
            try:
                # Timeout after 20 seconds (15s capture + buffer)
                if time.time() - start_time > 20:
                    break
                    
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                # Feedback to terminal
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        try:
            # We expect the command to be killed or timeout, so verify status
            os.kill(pid, 9)
            os.waitpid(pid, 0)
        except: pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- Starting Network Capture (Python Sniffer) on Pi ---")
    print("Monitoring UDP Port 10023 for 15 seconds...")
    print("Please move a fader on the Wing Mixer NOW!")
    
    # Run the Python sniffer we uploaded earlier
    # We first try to kill the bridge to free the port
    cmd = f"ssh -t {USER}@{HOST} 'echo START_SNIFF; python3 -u ~/behringer-mixer/simple_sniffer.py'"
    
    output = run_ssh_cmd(cmd)
    
    print("\n--- Capture Complete ---")
