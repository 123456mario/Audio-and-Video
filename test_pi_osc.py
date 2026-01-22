import socket
import time
import threading

WING_IP = "192.168.1.11"
WING_PORT = 2223
MY_PORT = 33901

def main():
    print(f"🕵️ Starting Simple OSC Test on Pi...")
    # 1. Create Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Force Bind
    
    # 2. Bind to FIXED port
    # Try 0.0.0.0 first (like Mac)
    try:
        sock.bind(('0.0.0.0', MY_PORT))
    except Exception as e:
        print(f"❌ Bind Error: {e}")
        return

    sock.settimeout(1.0) 
    
    print(f"👂 Listening on {MY_PORT} and Sending FROM {MY_PORT}...")
    
    # 3. Receiver Thread
    def receiver():
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                print(f"🎉 RESPONSE from {addr}: {data}")
            except:
                pass 
                
    t = threading.Thread(target=receiver, daemon=True)
    t.start()
    
    # 4. Send Queries using SAME socket
    queries = [
        b"/xremote\0\0\0\0", 
        b"/ch/1/fdr\0\0\0", 
        b"/ch/1/mute\0\0",
        b"/?\0\0"
    ]
    
    print(f"📤 Sending Queries to {WING_IP}:{WING_PORT}...")

    for q in queries:
        print(f"   Sending: {q}")
        sock.sendto(q, (WING_IP, WING_PORT))
        time.sleep(0.5)
        
    print("⏳ Waiting for responses (5s)...")
    time.sleep(5)
    print("✅ Done.")

if __name__ == "__main__":
    main()
