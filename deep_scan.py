import socket
import requests

TARGET_IP = "192.168.1.60"

print(f"🔎 Deep Scanning {TARGET_IP}...")

# 1. Check HTTP (Port 80) for Identity
print("\n[HTTP CHECK]")
try:
    response = requests.get(f"http://{TARGET_IP}", timeout=2)
    print(f"✅ Web Server Found!")
    print(f"   Server Header: {response.headers.get('Server', 'Unknown')}")
    print(f"   Title Snippet: {response.text[:100]}")
except Exception as e:
    print(f"❌ Web Check Failed: {e}")

# 2. Check UDP Ports (5200, 5000)
print("\n[UDP CHECK]")
udp_ports = [5200, 5000, 6666]
for port in udp_ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        # Send a dummy Novastar packet to provoke response
        # Read Mode Command
        dummy_cmd = bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 02 00 57 56") 
        sock.sendto(dummy_cmd, (TARGET_IP, port))
        
        try:
            data, addr = sock.recvfrom(1024)
            print(f"✅ UDP Port {port} responding! Data: {data.hex()}")
        except socket.timeout:
            print(f"   UDP Port {port}: No response within 1s")
    except Exception as e:
        print(f"❌ UDP Check Error on {port}: {e}")
