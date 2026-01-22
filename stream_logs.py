import pty
import os
import sys

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def stream():
    print(f"--- Streaming Logs from {HOST} ---")
    print("Move Wing Faders now! (Press Ctrl+C to stop)")
    
    # journalctl -f (follow) -u osc_bridge -n 10 (last 10 lines)
    cmd = f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S journalctl -f -u osc_bridge -n 10'"
    
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        try:
            while True:
                data = os.read(fd, 1024)
                if not data: break
                
                # Filter password
                if b"password" not in data.lower():
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
                
                if b"password:" in data.lower():
                    os.write(fd, f"{PASS}\n".encode())
                    
        except OSError:
            pass
        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    stream()
