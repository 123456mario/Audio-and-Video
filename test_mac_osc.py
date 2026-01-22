import socket
import time
import threading

WING_IP = "192.168.1.11"
WING_PORT = 2223
MY_PORT = 33900

def main():
    # 1. Create Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Bind to FIXED port
    sock.bind(('0.0.0.0', MY_PORT))
    sock.settimeout(1.0) # Non-blockingish
    
    print(f"👂 Listening on {MY_PORT} and Sending FROM {MY_PORT}...")
    
    # 3. Receiver Thread
    def receiver():
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                print(f"🎉 RESPONSE from {addr}: {data}")
            except:
                pass # Timeout
                
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
        
    print("⏳ Waiting more...")
    time.sleep(5)
    print("✅ Done.")

if __name__ == "__main__":
    main()
