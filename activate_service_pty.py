import pty
import os
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_with_pass(cmd):
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > 30: break
                data = os.read(fd, 1024)
                if not data: break
                output += data
                if b"password:" in data.lower():
                    os.write(fd, f"{PASS}\n".encode())
            except OSError:
                break
        try: os.waitpid(pid, 0)
        except: pass
        return output.decode('utf-8', errors='ignore')

def activate_service():
    print("--- ACTIVATING SYSTEMD SERVICE ---")
    
    # Sequence of commands to ensure service is running
    commands = [
        "sudo systemctl daemon-reload",
        "sudo systemctl enable wing_bridge.service",
        "sudo systemctl restart wing_bridge.service",
        "systemctl status wing_bridge.service --no-pager"
    ]
    
    for cmd in commands:
        full_ssh = f"ssh -t {USER}@{HOST} '{cmd}'"
        result = run_ssh_with_pass(full_ssh)
        print(result)
        print("-" * 20)

if __name__ == "__main__":
    activate_service()
