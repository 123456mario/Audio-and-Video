import argparse
import socket
from pythonosc.osc_packet import OscPacket

def print_packet(packet):
    for message in packet.messages:
        print(f"[{message.address}] {message.params}")

def run_sniffer(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    
    print(f"🎧 Listening for OSC UDP on {ip}:{port}...")
    
    try:
        while True:
            data, addr = sock.recvfrom(4096)
            print(f"\n📦 Received {len(data)} bytes from {addr}")
            try:
                packet = OscPacket(data)
                print_packet(packet)
            except Exception as e:
                print(f"⚠️ Raw Data (Decode Failed): {data}")
                print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sniff OSC UDP Packets")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="IP to bind to")
    parser.add_argument("--port", type=int, default=2223, help="Port to listen on")
    args = parser.parse_args()
    
    run_sniffer(args.ip, args.port)
