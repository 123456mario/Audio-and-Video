import requests

BASE_URL = "http://192.168.1.60:19999/unico/v1"
ENDPOINTS = [
    "node/power",
    "screen/image-quality",
    "ucenter/screen/image-quality",
    "ucenter/node/power",
    "screen/brightness",
    "system/info",
    "device/info",
    "cabinet/info-v2"
]

print(f"📡 Probing API at {BASE_URL}...\n")

for ep in ENDPOINTS:
    url = f"{BASE_URL}/{ep}"
    print(f"👉 Trying {url}...")
    try:
        r = requests.get(url, timeout=2)
        print(f"   Response {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ SUCCESS! Body: {r.text[:300]}")
        elif r.status_code == 404:
            print("   ❌ 404 Not Found")
        else:
            print(f"   ⚠️ Status {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print("-" * 40)
