import socket
import threading

PORT = 15000

def udp_listener():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', PORT))
        print(f"✅ UDP Listener active on {PORT}")
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"🚀 UDP RECEIVED from {addr}: {data}")
    except Exception as e:
        print(f"❌ UDP Error: {e}")

def tcp_listener():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', PORT))
        sock.listen(5)
        print(f"✅ TCP Listener active on {PORT}")
        while True:
            conn, addr = sock.accept()
            print(f"🔗 TCP CONNECTED from {addr}")
            try:
                data = conn.recv(1024)
                if data:
                    print(f"🚀 TCP RECEIVED: {data}")
                else:
                    print("⚠️ TCP Empty Data")
            except Exception as e:
                print(f"❌ TCP Read Error: {e}")
            finally:
                conn.close()
    except Exception as e:
        print(f"❌ TCP Error: {e}")

print(">>> UNIVERSAL SNIFFER STARTING <<<")
t1 = threading.Thread(target=udp_listener)
t2 = threading.Thread(target=tcp_listener)
t1.start()
t2.start()
t1.join()
t2.join()
