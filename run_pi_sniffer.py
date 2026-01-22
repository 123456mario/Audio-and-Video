import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        while True:
            try:
                # Capture for 10 seconds
                if time.time() - start_time > 10:
                    break
                    
                data = os.read(fd, 1024)
                if not data: break
                output += data
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
            except OSError:
                break
        
        # Kill the child process group to stop tcpdump if it's still running
        try:
            os.kill(pid, 9)
        except:
            pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- Sniffing UDP Port 10008 on Pi (10 seconds) ---")
    print("Please press the Xilica button NOW...")
    # Sudo is required for tcpdump
    cmd = f"ssh -t {USER}@{HOST} 'echo {PASS} | sudo -S tcpdump -i any udp port 10008 -XX -n'"
    run_ssh_cmd(cmd)
