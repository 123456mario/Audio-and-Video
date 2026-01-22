import socket
import time
import sys

WING_IP = "192.168.1.11"
WING_PORT = 2223
LISTEN_PORT = 50006  # Use a different port to avoid conflict

def discover():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0) # Non-blocking read with timeout
    
    # Bind to listening port
    try:
        sock.bind(('0.0.0.0', LISTEN_PORT))
        print(f"Listening on port {LISTEN_PORT}...")
    except Exception as e:
        print(f"Error binding: {e}")
        return

    # Send Subscription / Keep-Alive
    # OSC Message: "/xremote" + null padding + type tag string "," + null padding
    # /xremote is 8 bytes.
    # , is 1 byte, padded to 4 bytes -> ,000
    # Total: b'/xremote\x00\x00\x00\x00,000' usually.
    # Actually python-osc or similar lib is better for encoding, but raw is fine for simple strings.
    # Let's simple construct:
    # Address: /xremote (8 chars) -> null (1 char) -> pad to multiple of 4.
    # /xremote\x00\x00\x00\x00 (12 bytes)
    # Type tag: ,\x00\x00\x00 (4 bytes)
    # But usually just address is enough for some. 
    
    # Better: Use simple-osc library style encoding or just simple bytes if we know it.
    # /xremote is standard.
    msg = b'/xremote\x00\x00\x00\x00,\x00\x00\x00'
    
    print(f"Sending /xremote to {WING_IP}:{WING_PORT}...")
    try:
        sock.sendto(msg, (WING_IP, WING_PORT))
    except Exception as e:
        print(f"Send failed: {e}")

    print("\nXXX MOVE FADER NOW (Capturing for 30s) XXX\n")

    start = time.time()
    while time.time() - start < 30:
        try:
            # Resend keep-alive every 5 secs
            if int(time.time() - start) % 5 == 0:
                 sock.sendto(msg, (WING_IP, WING_PORT))

            data, addr = sock.recvfrom(1024)
            if addr[0] == WING_IP:
                # Decode OSC Address (simple string search)
                # Data starts with address string, null terminated
                parts = data.split(b'\x00')
                osc_addr = parts[0].decode('utf-8', errors='ignore')
                
                # Filter useful messages
                if "/fader" in osc_addr or "/on" in osc_addr or "/mute" in osc_addr:
                    print(f"!!! CAPTURED: {osc_addr}")
                    print(f"Full Data: {data}")
                    break # Found it!
                else:
                    print(f"Seen: {osc_addr}")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error: {e}")
            break
            
    print("Finished.")
    sock.close()

if __name__ == "__main__":
    discover()
