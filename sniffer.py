import socket
import struct

def sniff_udp(port):
    print(f"📡 Sniffing UDP Port {port}...", flush=True)
    
    # Create raw socket (Requires sudo)
    # AF_INET, SOCK_RAW, IPPROTO_UDP
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        sock.bind(("0.0.0.0", 0)) # Bind to all
    except PermissionError:
        print("❌ Sudo required!")
        return

    while True:
        try:
            raw_data, addr = sock.recvfrom(65535)
            
            # Parse IP Header (First 20 bytes)
            ip_header = raw_data[0:20]
            iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
            version_ihl = iph[0]
            ihl = version_ihl & 0xF
            iph_length = ihl * 4
            
            protocol = iph[6]
            s_addr = socket.inet_ntoa(iph[8])
            d_addr = socket.inet_ntoa(iph[9])

            if protocol == 17: # UDP
                udp_header = raw_data[iph_length:iph_length+8]
                udph = struct.unpack('!HHHH', udp_header)
                source_port = udph[0]
                dest_port = udph[1]
                
                # Filter by port 2223
                if source_port == port or dest_port == port:
                    print(f"🔥 Packet Detected: {s_addr}:{source_port} -> {d_addr}:{dest_port}")
                    payload = raw_data[iph_length+8:]
                    try:
                        print(f"   Payload (Text): {payload.decode('utf-8', 'ignore')}")
                    except:
                        pass
                    print(f"   Payload (Hex): {payload.hex()}")
                    print("-" * 30, flush=True)
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    sniff_udp(2223)
