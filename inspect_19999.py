import socket
import requests

TARGET_IP = "192.168.1.60"
PORT = 19999

print(f"🔎 Investigating Port {PORT} on {TARGET_IP}...")

# 1. Check TCP Connectivity
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    res = s.connect_ex((TARGET_IP, PORT))
    if res == 0:
        print(f"✅ TCP Port {PORT} is OPEN")
        s.close()
        
        # 2. Check HTTP
        try:
            url = f"http://{TARGET_IP}:{PORT}/web/unico/unicos/index.html"
            print(f"🌐 Fetching {url}...")
            r = requests.get(url, timeout=3)
            print(f"   Status: {r.status_code}")
            print(f"   Headers: {r.headers}")
            print(f"   Body Preview: {r.text[:200]}")
            
            # Check for API clues
            if "login" in r.text.lower():
                print("   🔑 Login required")
        except Exception as e:
            print(f"❌ HTTP Fetch Failed: {e}")

    else:
        print(f"❌ TCP Port {PORT} is Closed")
except Exception as e:
    print(f"⚠️ Error checking port: {e}")

# 3. UDP Probe on 19999 (Just in case)
print(f"📡 Probing UDP {PORT}...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    PING_CMD = bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56")
    sock.sendto(PING_CMD, (TARGET_IP, PORT))
    data, addr = sock.recvfrom(1024)
    print(f"✅ UDP RESPONSE on {PORT}: {data.hex()}")
except socket.timeout:
    print(f"❌ No response on UDP {PORT}")
except Exception as e:
    print(f"⚠️ Error on UDP: {e}")
