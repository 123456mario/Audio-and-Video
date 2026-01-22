import requests

BASE_URL = "http://192.168.1.60:19999/unico/v1/node/power"
# Common or likely header names based on Chinese error "Please pass the IP you want to proxy in headers"
HEADER_CANDIDATES = [
    "ip", "IP", "Target-IP", "target-ip", "TargetIp",
    "Proxy-IP", "proxy-ip", "ProxyIp",
    "Device-IP", "device-ip", "DeviceIp",
    "Node-IP", "NodeIp", 
    "X-Forwarded-For", "X-Target-IP",
    "dest-ip", "DestIp",
    "host-ip", "HostIp"
]

TARGET_IPS = ["127.0.0.1", "192.168.1.60", "localhost"]

print(f"📡 Fuzzing Headers for {BASE_URL}...\n")

success = False
for h_name in HEADER_CANDIDATES:
    for ip in TARGET_IPS:
        headers = {h_name: ip}
        try:
            r = requests.get(BASE_URL, headers=headers, timeout=1)
            # If we get anything other than 500 with the exact same error, it's a lead
            if "请在headers中传入" not in r.text:
                print(f"🔥 POTENTIAL HIT! Header: '{h_name}: {ip}'")
                print(f"   Status: {r.status_code}")
                print(f"   Body: {r.text[:200]}")
                success = True
                break
        except:
            pass
    if success: break

if not success:
    print("❌ No luck with common header names.")
