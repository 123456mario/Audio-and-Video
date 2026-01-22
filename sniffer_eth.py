import socket
import struct

def sniff_eth():
    print("📡 Sniffing Ethernet (Outgoing & Incoming)...", flush=True)
    
    # AF_PACKET captures everything at Layer 2
    # ETH_P_ALL = 0x0003
    sock = None
    interfaces = ["eth0", "wlan0", "en0", "lo"]
    
    for iface in interfaces:
        try:
            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            s.bind((iface, 0))
            print(f"✅ Bound to interface: {iface}")
            sock = s
            break
        except Exception as e:
            # print(f"⚠️ Could not bind to {iface}: {e}")
            pass
            
    if not sock:
        print("❌ Could not bind to any interface (eth0, wlan0). Run with SUDO?")
        return

    while True:
        try:
            raw_data, _ = sock.recvfrom(65535)
            
            # Ethernet Header (14 bytes)
            eth_header = raw_data[:14]
            dest_mac, src_mac, eth_proto = struct.unpack('!6s6sH', eth_header)
            
            if eth_proto == 0x0800: # IPv4
                ip_header = raw_data[14:34]
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                protocol = iph[6]
                s_addr = socket.inet_ntoa(iph[8])
                d_addr = socket.inet_ntoa(iph[9])
                
                # UDP Header Analysis
                if protocol == 17: # UDP
                    ihl = (iph[0] & 0xF) * 4
                    udp_offset = 14 + ihl
                    udp_header = raw_data[udp_offset:udp_offset+8]
                    udph = struct.unpack('!HHHH', udp_header)
                    
                    src_port = udph[0]
                    dst_port = udph[1]

                    # Filter: Wing (2223)
                    if src_port == 2223 or dst_port == 2223:
                        direction = "📤 OUT (UDP)" if d_addr == "192.168.1.11" else "📥 IN (UDP)"
                        print(f"{direction} {s_addr}:{src_port} -> {d_addr}:{dst_port}")
                        
                        payload = raw_data[udp_offset+8:]
                        print(f"   Hex: {payload.hex()}")
                        try: print(f"   Txt: {payload.decode('utf-8', 'ignore')}")
                        except: pass
                        print("-" * 30, flush=True)

                # TCP Header Analysis (For Xilica)
                elif protocol == 6: # TCP
                    ihl = (iph[0] & 0xF) * 4
                    tcp_offset = 14 + ihl
                    # TCP Header is at least 20 bytes
                    tcp_header = raw_data[tcp_offset:tcp_offset+20]
                    tcph = struct.unpack('!HHLLBBHHH', tcp_header)
                    
                    src_port = tcph[0]
                    dst_port = tcph[1]
                    
                    # Filter: Xilica Bridge (1500)
                    if src_port == 1500 or dst_port == 1500:
                        direction = "📥 FROM Xilica" if dst_port == 1500 else "📤 TO Xilica"
                        print(f"🔗 {direction} {s_addr}:{src_port} -> {d_addr}:{dst_port}")
                        
                        # Payload calculation is trickier for TCP (Header Length)
                        data_offset = (tcph[4] >> 4) * 4
                        payload = raw_data[tcp_offset+data_offset:]
                        
                        if len(payload) > 0:
                            try: 
                                txt = payload.decode('utf-8', 'ignore').strip()
                                if txt: print(f"   Msg: {txt}")
                            except: pass
                        print("-" * 30, flush=True)
                    
                    payload = raw_data[udp_offset+8:]
                    print(f"   Hex: {payload.hex()}")
                    try:
                         print(f"   Txt: {payload.decode('utf-8', 'ignore')}")
                    except: pass
                    print("-" * 30, flush=True)

        except KeyboardInterrupt:
            break
        except Exception as e:
            pass # Ignore malformed

if __name__ == "__main__":
    sniff_eth()
