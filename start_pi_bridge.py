import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_interactive(cmd):
    print(f"Connecting to {HOST} to run: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/usr/bin/ssh", ["/usr/bin/ssh", f"{USER}@{HOST}", cmd])
    else:
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                if b"password:" in data.lower():
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in data.lower():
                    os.write(fd, b"yes\n")
            except OSError:
                break
        _, status = os.waitpid(pid, 0)

if __name__ == "__main__":
    # Run the bridge script explicitly using bash to ensure profile/venv loading if needed,
    # though run_bridge.sh handles venv activation.
    # We use -t to force tty allocation if we want interactive control, 
    # but for just running it, ordinary exec is fine. 
    # run_bridge.sh is executable.
    run_ssh_interactive("~/behringer-mixer/run_bridge.sh")
