import socket

HOST = '0.0.0.0'
PORT = 1500

def main():
    print(f"🕵️ TCP Sniffer Listening on {HOST}:{PORT}...")
    print("Waiting for Xilica to connect...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"🔗 Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"📥 Received data: {data}")
                    try:
                        print(f"📄 Decoded: {data.decode('utf-8').strip()}")
                    except:
                        pass
        except OSError as e:
            print(f"❌ Error: {e}")
            print("Check if port 1500 is already in use (the bridge might be running).")

if __name__ == "__main__":
    main()
