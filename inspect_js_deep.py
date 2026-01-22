import requests
import re

URL = "http://192.168.1.60:19999/web/unico/unicos/static/main-CpDeOf7C.js"

print("Downloading main.js...")
r = requests.get(URL)
content = r.text

print("Searching for HTTP/WS methods...")
# Search for .post( or .get( or fetch(
patterns = [
    r'\.post\s*\(\s*["\']([^"\']+)["\']',
    r'\.get\s*\(\s*["\']([^"\']+)["\']',
    r'fetch\s*\(\s*["\']([^"\']+)["\']',
    r'url\s*:\s*["\']([^"\']+)["\']'
]

found = set()
for p in patterns:
    matches = re.findall(p, content)
    for m in matches:
        if len(m) < 100: # Filter out garbage
             found.add(m)

print(f"Found {len(found)} URL paths:")
for f in list(found)[:20]:
    print(f" - {f}")

# Look for specific "brightness" API calls
# Context around "brightness"
idx = content.find("setScreenBrightness")
if idx != -1:
    print(f"\nContext around 'setScreenBrightness':\n{content[idx-100:idx+200]}")
