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
        start_t = time.time()
        while (time.time() - start_t) < 20: # 20s timeout
            try:
                data = os.read(fd, 1024)
                if not data: break
                
                # Print live
                sys.stdout.write(data.decode('utf-8', errors='ignore'))
                sys.stdout.flush()
                output += data
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        # Cleanup
        try:
           os.kill(pid, 9)
        except: pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print(f"--- RUNNING TCPDUMP ON PI ({HOST}) ---")
    print("Listening on UDP ports 10010-10030 for 15 seconds...")
    print(">> PLEASE PRESS LIGHTING BUTTONS ON XILICA NOW <<")
    
    # Run tcpdump on ANY interface, UDP, ports 10010-10030
    # -n: Don't resolve hostnames
    # -X: Show payload in hex and ASCII
    cmd = f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S tcpdump -i any -n -X udp portrange 10010-10030'"
    
    run_ssh_cmd(cmd)
    print("\n--- DONE ---")
