import pty
import os
import sys
import time

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

SNIFFER_CODE = r"""
import socket
import threading
import time

def sniff(port):
    print(f"Starting listener on {port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"🟢 [{port}] HIT! From {addr} | Length: {len(data)} | Hex: {data.hex()}")
    except OSError as e:
        if e.errno == 98:
            print(f"🔴 [{port}] Port ALREADY IN USE! Something is running here.")
        else:
            print(f"[{port}] ERROR: {e}")
    except Exception as e:
        print(f"[{port}] ERROR: {e}")

if __name__ == "__main__":
    print("=== DUAL PORT SNIFFER (10012 & 10021) ===")
    t1 = threading.Thread(target=sniff, args=(10012,))
    t2 = threading.Thread(target=sniff, args=(10021,))
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
    time.sleep(20)
    print("=== TIMEOUT REACHED ===")
"""

def run_ssh_cmd(cmd):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        start_t = time.time()
        while (time.time() - start_t) < 25: # 25s timeout
            try:
                data = os.read(fd, 1024)
                if not data: break
                
                sys.stdout.write(data.decode('utf-8', errors='ignore'))
                sys.stdout.flush()
                output += data
                
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
                if b"continue connecting" in low_data:
                    os.write(fd, b"yes\n")
            except OSError:
                break
        
        try: os.kill(pid, 9)
        except: pass
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print(f"--- DEPLOYING & RUNNING SNIFFER ON {HOST} ---")
    
    # 1. Stop Bridge
    print("1. Kill existing bridge...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {PASS} | sudo -S pkill -f artnet_bridge.py'")
    
    # 2. Write File
    # We use a simple echo strategy but escape quotes carefully or use Base64? 
    # Base64 is safer.
    import base64
    b64_code = base64.b64encode(SNIFFER_CODE.encode("utf-8")).decode("utf-8")
    
    print("2. Writing sniffer code...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'echo {b64_code} | base64 -d > /home/pi/behringer-mixer/temp_sniffer.py'")
    
    # 3. Run
    print("3. RUNNING SNIFFER (20s)...")
    run_ssh_cmd(f"ssh {USER}@{HOST} 'python3 -u /home/pi/behringer-mixer/temp_sniffer.py'")
    
    print("\n--- FINISHED ---")
