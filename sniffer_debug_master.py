import socket

HOST = '0.0.0.0'
PORT = 10025

def start_sniffer():
    print(f"🕵️ STARTING SNIFFER ON PORT {PORT}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind((HOST, PORT))
        s.listen(1)
        print("✅ Listening... Waiting for Xilica...")
        
        while True:
            conn, addr = s.accept()
            print(f"🔗 Connected by {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data: 
                        print("❌ Disconnected")
                        break
                    print(f"📥 RAW DATA: {data}")
                    try:
                        print(f"📝 TEXT: {data.decode('utf-8', errors='ignore')}")
                    except: pass
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    start_sniffer()
