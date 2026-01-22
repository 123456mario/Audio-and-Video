import pty
import os
import sys

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
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
    print(f"--- Running OSC Discovery on ({HOST}) ---")
    # Execute python -u to ensure unbuffered output
    # Kill previous instance first
    cmd = f"ssh {USER}@{HOST} 'pkill -f discover_wing.py; cd behringer-mixer && ./venv/bin/python -u discover_wing.py'"
    print(run_ssh_cmd(cmd))
