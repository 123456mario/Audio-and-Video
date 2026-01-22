import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def capture_traffic():
    print(f"--- DEEP PACKET CAPTURE: ALL TRAFFIC FROM {HOST} ---")
    print("Capturing EVERYTHING from Source IP 192.168.1.20...")
    print("Please move Master Fader/Mute NOW!")
    
    # tcpdump arguments:
    # -i eth0: listen on ethernet
    # -n: don't resolve hostnames
    # -A: print ASCII (good for text commands)
    # -v: verbose
    # src 192.168.1.20: only packets coming FROM Xilica
    cmd = f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S tcpdump -i any -n -A src 192.168.1.20'"
    
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        try:
            while True:
                # Read output
                try:
                    data = os.read(fd, 1024)
                    if not data: break
                    
                    low_data = data.lower()
                    # Filter password prompt
                    if b"password" not in low_data:
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
                    
                    if b"password:" in low_data:
                        os.write(fd, f"{PASS}\n".encode())
                    
                    # Run for 25 seconds
                    if time.time() - start_time > 25:
                        print("\n--- Capture Timeout (25s) ---")
                        break
                        
                except OSError:
                    break
        except KeyboardInterrupt:
            print("\n--- Interrupted ---")
        
        # Cleanup
        os.kill(pid, 9)
        os.waitpid(pid, 0)
        print("--- CAPTURE DONE ---")

if __name__ == "__main__":
    capture_traffic()
