import requests
import re

URL = "http://192.168.1.60:19999/web/unico/unicos/static/main-CpDeOf7C.js"

print("Downloading main.js...")
r = requests.get(URL)
content = r.text

print("Searching for 'headers' definitions...")
# Look for object keys like `headers:{...}` or `headers: {`
# Capture the content inside basic brackets
matches = re.findall(r'headers\s*:\s*\{([^}]+)\}', content)

print(f"Found {len(matches)} header blocks. Checking typical ones...")
for m in matches[:20]:
    print(f" - {m.strip()}")

# Also look for the specific error string or related keys
if "ip" in content.lower():
    # Try to find where "ip" is added to headers
    # Look for `.ip =` or `['ip'] =`
    print("\nChecking for explicit 'ip' assignment:")
    ip_assigns = re.findall(r'["\']ip["\']\s*:\s*', content)
    if ip_assigns:
        print(f"   Found 'ip' key assignment: {len(ip_assigns)} times")
