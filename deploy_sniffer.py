import pty
import os
import sys

# Connection details (From deploy_to_pi.py)
HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    print(f"Running: {cmd}")
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
                
                # Check for password prompt if needed (though sshpass or keys are better, this follows existing pattern)
                if b"password:" in data.lower():
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in data.lower():
                    os.write(fd, b"yes\n")
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

def main():
    print("=== Deploying UDP Sniffer ===")
    
    # Transfer
    cmd_scp = f"scp udp_sniffer.py {USER}@{HOST}:~/behringer-mixer/"
    print(run_ssh_cmd(cmd_scp))
    
    # Kill existing bridge to free up port
    print("--- Stopping existing bridge ---")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f artnet_bridge.py'")
    
    # Run Sniffer
    print("--- Starting Sniffer ---")
    print("Check the output below. Move the Xilica Fader NOW!")
    
    # We run slightly differently to see output
    cmd_run = f"ssh {USER}@{HOST} 'python3 ~/behringer-mixer/udp_sniffer.py'"
    
    # Note: This will block until Ctrl+C, showing output
    # But since we are calling it via run_ssh_cmd which captures output, 
    # we might not see it in real-time if buffering happens.
    # However, for a quick test it's fine.
    
    # Better: Open a separate terminal for the user?
    # Or just tell user to run it.
    
    print(f"Run this command on your Pi or via ssh:\npython3 ~/behringer-mixer/udp_sniffer.py")
    
    # Let's just run it for 10 seconds timeout or similar? No, user needs to test.
    # I'll just deploy it and tell user how to run.

if __name__ == "__main__":
    main()
