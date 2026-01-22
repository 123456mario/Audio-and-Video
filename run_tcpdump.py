import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_tcpdump():
    print(f"--- Remote Packet Capture on Pi ({HOST}) ---")
    print("Capturing UDP traffic on ports 10023 and 2223...")
    print("Move the Wing Faders NOW!")
    
    # tcpdump -l (buffered), -n (no DNS), -i any (all interfaces)
    cmd = f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S tcpdump -i any -n -l udp port 10023 or udp port 2223'"
    
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
                    
                    # Filter password prompt visually
                    if b"password" not in data.lower():
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
                    
                    # Handle Password
                    if b"password:" in data.lower():
                        os.write(fd, f"{PASS}\n".encode())
                    
                    # Timeout after 15 seconds of capturing
                    if time.time() - start_time > 20:
                        print("\n--- Capture Timeout (20s) ---")
                        break
                        
                except OSError:
                    break
        except KeyboardInterrupt:
            print("\n--- Interrupted ---")
        
        # Cleanup
        os.kill(pid, 9)
        os.waitpid(pid, 0)

if __name__ == "__main__":
    run_tcpdump()
