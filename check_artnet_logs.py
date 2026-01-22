import pty
import os
import sys
import socket

# Raspberry Pi Credentials
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
    print(f"--- RESTARTING Art-Net Bridge on Pi ({HOST}) with DEBUG LOGGING ---")
    
    # 1. Kill existing
    print("1. Killing existing process...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'pkill -f artnet_bridge.py'")
    
    # 2. Start with logging
    print("2. Starting with logging (debug_bridge.log)...")
    # nohup python3 -u (unbuffered) ...
    run_ssh_cmd(f"ssh {USER}@{HOST} 'nohup python3 -u /home/pi/behringer-mixer/artnet_bridge.py > /home/pi/behringer-mixer/debug_bridge.log 2>&1 < /dev/null &'")
    
    import time
    
    print("3. Waiting 2 seconds before sending TEST PACKET...")
    time.sleep(2)
    
    # --- INJECT TEST PACKET ---
    print("   >> SENDING TEST PACKET (Universe 0, Value 255) to 192.168.1.50:10021...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'\x00\xFF', (HOST, 10021))
        # Send a text packet too for good measure
        sock.sendto(b'UNIV:0 VAL:255', (HOST, 10021))
        sock.close()
        print("   >> PACKETS SENT.")
    except Exception as e:
        print(f"   >> FAILED TO SEND PACKET: {e}")
    # --------------------------
    
    print("4. Waiting 5 more seconds for processing...")
    time.sleep(5)
    
    # 3. Read Log
    print("5. Reading Log:")
    log_out = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 20 /home/pi/behringer-mixer/debug_bridge.log'")
    print(log_out)
