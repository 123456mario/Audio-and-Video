import socket
import threading
import time
import sys

TARGET_IP = "192.168.1.11"
SCAN_DURATION = 15 # seconds

# Ports to probe
# 1. Known defaults
PORTS = [2222, 2223]
# 2. X32/M32 legacy ports
PORTS += [10023, 10024]
# 3. Standard OSC
PORTS += [8000, 9000]
# 4. Dense range around defaults
PORTS += list(range(2200, 2250))

print(f"--- Behringer Wing Port Scanner ---")
print(f"Target: {TARGET_IP}")
print(f"Scanning {len(PORTS)} ports...")

# Shared socket for Send/Recv
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)
sock.bind(('0.0.0.0', 0)) # Bind to ephemeral port
my_port = sock.getsockname()[1]
print(f"Scanner listening on local port: {my_port}")

stop_event = threading.Event()
found_ports = set()

def receiver():
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(4096)
            if addr[0] == TARGET_IP:
                print(f"\n[SUCCESS] Response from {addr}: {len(data)} bytes")
                found_ports.add(addr[1])
        except socket.timeout:
            continue
        except Exception as e:
            if not stop_event.is_set():
                print(f"Receive error: {e}")
            break

def sender():
    # OSC Probes:
    # 1. /xremote (Subscription)
    probe_xremote = b'/xremote\x00\x00\x00\x00,\x00\x00\x00'
    # 2. /? (Info/Handshake)
    probe_info = b'/?\x00\x00'
    # 3. / (Root)
    probe_root = b'/\x00\x00\x00'

    for _ in range(3): # Repeat passes
        if stop_event.is_set(): break
        for port in PORTS:
            if stop_event.is_set(): break
            try:
                sock.sendto(probe_xremote, (TARGET_IP, port))
                sock.sendto(probe_info, (TARGET_IP, port))
                sock.sendto(probe_root, (TARGET_IP, port))
                # Small delay to prevent flooding buffer
                time.sleep(0.005)
            except Exception as e:
                print(f"Send error on {port}: {e}")
        time.sleep(1)

# Start Threads
t_recv = threading.Thread(target=receiver)
t_recv.daemon = True
t_recv.start()

t_send = threading.Thread(target=sender)
t_send.daemon = True
t_send.start()

# Main Wait
try:
    for i in range(SCAN_DURATION):
        sys.stdout.write(f"\rScanning... {SCAN_DURATION - i}s")
        sys.stdout.flush()
        time.sleep(1)
except KeyboardInterrupt:
    pass

stop_event.set()
print("\n--- Scan Complete ---")

if found_ports:
    print(f"✅ FOUND OPEN PORTS ON WING: {sorted(list(found_ports))}")
else:
    print("❌ No response received from any port.")
