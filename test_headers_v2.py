import requests

BASE_URL = "http://192.168.1.60:19999/unico/v1/node/power"
# Also try screen info which might be read-only
INFO_URL = "http://192.168.1.60:19999/unico/v1/screen/image-quality"

CANDIDATES = [
    {"ip": "127.0.0.1", "port": "80", "protocol": "http"},
    {"ip": "127.0.0.1", "port": "19999", "protocol": "http"},
    {"ip": "192.168.1.60", "port": "80", "protocol": "http"},
    {"ip": "192.168.1.60", "port": "19999", "protocol": "http"},
    # Maybe port 5200 internal?
    {"ip": "127.0.0.1", "port": "5200", "protocol": "tcp"}, 
]

print(f"📡 Testing Complex Headers against {BASE_URL}...\n")

for headers in CANDIDATES:
    print(f"👉 Sending Headers: {headers}")
    try:
        # Try both Node Power and Info
        for url in [BASE_URL, INFO_URL]:
            r = requests.get(url, headers=headers, timeout=2)
            if "请在headers中传入" not in r.text and r.status_code != 500:
                print(f"   ✅ SUCCESS! Status: {r.status_code}")
                print(f"   Body: {r.text[:300]}")
            elif r.status_code == 200: # Sometimes 200 OK but with error code in JSON
                 print(f"   ⚠️ 200 OK but maybe error: {r.text[:150]}")
            else:
                 print(f"   ❌ Failed: {r.status_code} - {r.text[:100]}")
            print("   ---")
    except Exception as e:
        print(f"   ❌ Network Error: {e}")
