import pty
import os
import sys

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    # print(f"Running (Remote): {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        # Child
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        # Parent
        output = b""
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                # Automated password handling (silent)
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        try:
            _, status = os.waitpid(pid, 0)
        except ChildProcessError:
            pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- Fetching Logs from Pi ---")
    log_content = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 50 ~/behringer-mixer/bridge_log.txt'")
    
    # Filter out ssh banner/password prompt clutter if possible, or just print all
    lines = log_content.splitlines()
    for line in lines:
        if "password:" in line.lower(): continue
        if "Last login:" in line: continue
        print(line)
