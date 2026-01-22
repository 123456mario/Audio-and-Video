import requests
import re

BASE_URL = "http://192.168.1.60:19999/web/unico/unicos"
FILES = [
    "config.js",
    "static/index-B69W3Tnd.js",
    "static/main-CpDeOf7C.js"
]

print("🔎 Analyzing JS for APIs...")

for f in FILES:
    url = f"{BASE_URL}/{f}"
    print(f"\n📂 Fetching {url}...")
    try:
        r = requests.get(url, timeout=5)
        content = r.text
        print(f"   Size: {len(content)} bytes")
        
        # Search for API-like patterns
        # 1. Look for "/api/..."
        apis = re.findall(r'["\'](/api/[^"\']+)["\']', content)
        if apis:
            print(f"   🎯 Found APIs: {apis[:5]}")
            
        # 2. Look for "brightness" or "screen" related keys
        keywords = ["brightness", "blackscreen", "screenpower", "setbrightness", "set_screen_power"]
        for k in keywords:
            if k in content.lower():
                print(f"   ✨ Found keyword '{k}':")
                # specific context (20 chars around)
                start_idx = content.lower().find(k)
                print(f"      ...{content[start_idx-20:start_idx+60]}...")

    except Exception as e:
        print(f"❌ Failed to fetch {f}: {e}")
