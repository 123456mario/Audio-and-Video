import socket
import requests
import time

TARGET_IP = "192.168.1.60"

# Known Magic Packet for "Read Mode" (Safe Ping)
# 55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56
PING_CMD = bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56")

def check_http():
    print(f"\n🌐 Checking HTTP on {TARGET_IP}:80...")
    try:
        r = requests.get(f"http://{TARGET_IP}", timeout=2)
        print(f"✅ HTTP Response: {r.status_code}")
        print(f"   Server: {r.headers.get('Server', 'Unknown')}")
        print(f"   Content: {r.text[:100]}...")
    except Exception as e:
        print(f"❌ HTTP Failed: {e}")

def check_udp_port(port):
    print(f"📡 Probing UDP Port {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    try:
        sock.sendto(PING_CMD, (TARGET_IP, port))
        data, addr = sock.recvfrom(1024)
        print(f"✅ UDP RESPONSE on Port {port}: {data.hex()}")
        return True
    except socket.timeout:
        print(f"❌ No response on UDP {port}")
    except Exception as e:
        print(f"⚠️ Error on UDP {port}: {e}")
    finally:
        sock.close()
    return False

def check_tcp_port(port):
    print(f"🔗 Checking TCP Port {port}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        res = s.connect_ex((TARGET_IP, port))
        if res == 0:
            print(f"✅ TCP Port {port} is OPEN")
        else:
            print(f"❌ TCP Port {port} is Closed/Filtered")
        s.close()
    except:
        pass

print(f"=== Starting Deep Diagnosis for {TARGET_IP} ===")

# 1. HTTP Check (to identify device)
check_http()

# 2. TCP Check (Re-verify)
check_tcp_port(15200) # Manual says 15200
check_tcp_port(5200)
check_tcp_port(6666)

# 3. UDP Probe (Send Ping to provoke response)
check_udp_port(15200)
check_udp_port(5200)
check_udp_port(6666)

print("=== Diagnosis Complete ===")
