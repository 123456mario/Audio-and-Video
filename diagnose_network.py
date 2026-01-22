import pty
import os
import sys

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"
WING_IP = "192.168.1.11"

def run_ssh_cmd(cmd):
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
                # Stream output
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
        return output.decode('utf-8', errors='ignore')

def diagnose():
    print(f"--- Diagnosing Network Connection to Wing ({WING_IP}) ---")
    
    # 1. Ping
    print(f"\n1. Pinging Wing at {WING_IP}...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'ping -c 4 {WING_IP}'")
    
    # 2. Check ARP table
    print(f"\n2. ARP Table Check:")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'arp -n'")
    
    # 3. Check Pi's IP config
    print(f"\n3. Pi IP Configuration:")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'ip addr'")

if __name__ == "__main__":
    diagnose()
