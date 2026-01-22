import socket
import sys
import time
import threading

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 10023

WING_IP = "192.168.1.11"
WING_PORT = 2222

print(f"--- Active UDP Sniffer for Port {LISTEN_PORT} ---")
print(f"Target Wing: {WING_IP}:{WING_PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind((LISTEN_IP, LISTEN_PORT))
except Exception as e:
    print(f"Error binding to port {LISTEN_PORT}: {e}")
    sys.exit(1)

# Subscription Thread
def send_subscription():
    # /xremote command (padded to 4 bytes boundary)
    # String "/xremote" + 0x00 + "," + 0x00 * 3
    # Actually just ensuring packet structure is valid enough for Wing
    # Simple PythonOSC style: address + type tag string...
    # But raw bytes usually work: b"/xremote\0\0\0\0,\0\0\0"
    msg = b'/xremote\x00\x00\x00\x00,\x00\x00\x00'
    
    print("Starting subscription loop...")
    while True:
        try:
            sock.sendto(msg, (WING_IP, WING_PORT))
            # print("Sent /xremote req")
        except Exception as e:
            print(f"Send error: {e}")
        time.sleep(2)

t = threading.Thread(target=send_subscription)
t.daemon = True
t.start()

print("Waiting for packets (Move Faders Now!)...")

# Loop for a bit or until interrupted
start_time = time.time()
packet_count = 0

try:
    sock.settimeout(1.0) # 1 second timeout to check for exit
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            packet_count += 1
            print(f"[{time.strftime('%H:%M:%S')}] RECEIVED {len(data)} bytes from {addr}")
            # Try to decode as generic text to see address
            try:
                decoded = data.decode('utf-8', errors='ignore')
                # Filter printable chars roughly
                clean = "".join([c if c.isprintable() else '.' for c in decoded])
                print(f"    Payload: {clean}")
            except:
                pass
            sys.stdout.flush()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error reading: {e}")
            break
except KeyboardInterrupt:
    print("\nStopping sniffer.")
finally:
    sock.close()
