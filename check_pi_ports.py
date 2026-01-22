import pty
import os
import sys

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

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

if __name__ == "__main__":
    # Check if we are listening on 0.0.0.0
    run_ssh_cmd(f"ssh {USER}@{HOST} 'netstat -uln | grep 10008'")
    # Also cat the file to be sure
    run_ssh_cmd(f"ssh {USER}@{HOST} 'grep LISTEN_IP ~/behringer-mixer/novastar_bridge.py'")
