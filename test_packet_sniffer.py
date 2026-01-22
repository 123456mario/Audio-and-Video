import socket
import struct

# Listen on ALL interfaces
IP = "0.0.0.0"
# We want to see traffic on the Wing Port and our Bridge Port
# But raw sockets in Python usually need ROOT.
# Instead, we can bind to the port and print what we receive.
# BUT we can't bind to 2223 (Wing is not here) or 33859 (Bridge is using it).
# So we have to stop the bridge first to use this sniffer on 33859.

PORT = 33860 # Alternative port to avoid conflict

def main():
    print(f"🕵️ Starting Packet Sniffer on Port {PORT}...")
    print("⚠️  NOTE: Stop the main osc_bridge service first! (sudo systemctl stop osc_bridge)")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((IP, PORT))
    except OSError:
        print(f"❌ Port {PORT} is busy. Did you stop osc_bridge?")
        return

    print("✅ Listening... Move a fader on the Wing Console NOW!")
    
    # Send a query to provoke a response (Manual Poll)
    wing_ip = "192.168.1.11"
    wing_port = 2223
    query = b"/ch/1/fdr\0\0\0" # Simple Query
    
    print(f"📤 Sending test query to {wing_ip}:{wing_port}...")
    sock.sendto(query, (wing_ip, wing_port))

    while True:
        data, addr = sock.recvfrom(4096)
        print(f"\n📨 Received {len(data)} bytes from {addr}:")
        
        # Hex Dump
        print(f"   Hex: {data.hex()}")
        
        # ASCII Dump (Try to read OSC address)
        try:
            txt = data.decode('latin-1', errors='ignore')
            clean_txt = "".join([c if c.isprintable() else '.' for c in txt])
            print(f"   Txt: {clean_txt}")
            
            # Check for float value
            if len(data) >= 4:
                val = struct.unpack('>f', data[-4:])[0]
                print(f"   Float Val: {val}")
        except:
            pass

if __name__ == "__main__":
    main()
