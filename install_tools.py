import pty
import os
import sys

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def install():
    print(f"--- Installing tcpdump on {HOST} ---")
    
    # apt-get update and install
    cmd = f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S apt-get update && echo {PASS} | sudo -S apt-get install -y tcpdump'"
    
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        while True:
            try:
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
        
        _, status = os.waitpid(pid, 0)
        
    print("\n--- Installation Attempt Complete ---")

if __name__ == "__main__":
    install()
