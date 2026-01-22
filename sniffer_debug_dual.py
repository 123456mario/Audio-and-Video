import socket
import threading
import time

def sniff(port):
    print(f"Starting listener on {port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse if hung
        sock.bind(('0.0.0.0', port))
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"🟢 [{port}] HIT! From {addr} | Len: {len(data)} | Hex: {data.hex()}")
    except OSError as e:
        if e.errno == 98:
            print(f"🔴 [{port}] Port ALREADY IN USE! Something else is running here.")
        else:
            print(f"[{port}] ERROR: {e}")
    except Exception as e:
        print(f"[{port}] ERROR: {e}")

if __name__ == "__main__":
    print("=== DUAL PORT SNIFFER (10012 & 10021) ===")
    
    t1 = threading.Thread(target=sniff, args=(10012,))
    t2 = threading.Thread(target=sniff, args=(10021,))
    
    t1.daemon = True # Allow main thread exit to kill them
    t2.daemon = True
    
    t1.start()
    t2.start()
    
    # Run for 20 seconds then exit
    time.sleep(20)
    print("=== TIMEOUT REACHED ===")
