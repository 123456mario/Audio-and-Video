import socket
import time

HOST = "0.0.0.0"
PORT = 2223

def sniff():
    print(f"--- 🕵️ Simple UDP Sniffer on Port {PORT} ---")
    print("Waiting for packets... (Move a fader on the Wing!)")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((HOST, PORT))
        sock.settimeout(15.0) # 15s timeout
        
        start_t = time.time()
        while time.time() - start_t < 15:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"[{time.strftime('%H:%M:%S')}] 📦 From {addr}: {data}")
            except socket.timeout:
                pass
    except Exception as e:
        print(f"Error: {e}")
        print("Note: If 'Address already in use', the main bridge is running.")
        print("This is good! It means the port is bound.")
        print("To sniff raw bytes, we'd need to stop the bridge first or use tcpdump (which failed).")
        print("BUT, if the bridge is running, check the LOGS instead.")
        
    finally:
        sock.close()
        print("--- Sniffer Closed ---")

if __name__ == "__main__":
    sniff()
