import pty
import os
import sys

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    # print(f"Executing: {cmd}")
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
    print(f"--- Diagnosing Pi ({HOST}) Status ---")
    
    print("\n1. Checking osc_bridge service status:")
    service_status = run_ssh_cmd(f"ssh {USER}@{HOST} 'systemctl status osc_bridge'")
    print(service_status)
    
    print("\n2. Checking recent service logs (journalctl):")
    # Get last 50 lines of logs for the service
    logs = run_ssh_cmd(f"ssh {USER}@{HOST} 'journalctl -u osc_bridge -n 50 --no-pager'")
    print(logs)
    
    print("\n3. Checking for active python processes:")
    ps_output = run_ssh_cmd(f"ssh {USER}@{HOST} 'ps aux | grep python'")
    print(ps_output)
