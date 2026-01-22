import pty
import os
import sys
import time

# Raspberry Pi Credentials
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running (Remote): {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        # Child
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        # Parent
        output = b""
        start_time = time.time()
        while True:
            try:
                # Timeout after 60 seconds (loop is long)
                if time.time() - start_time > 60:
                    break
                    
                data = os.read(fd, 1024)
                if not data: break
                output += data
                
                # Feedback to terminal
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        try:
            os.kill(pid, 9)
            os.waitpid(pid, 0)
        except: pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    # Upload
    print("--- Uploading Auto-Tester ---")
    run_ssh_cmd(f"scp /Users/gimdongseong/Documents/GitHub/behringer-mixer/auto_tester.py {USER}@{HOST}:~/behringer-mixer/")
    
    # Run
    print("--- Running Auto-Tester Loop ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'python3 -u ~/behringer-mixer/auto_tester.py'")
