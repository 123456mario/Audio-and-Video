import requests

ip = "192.168.1.60"
try:
    resp = requests.get(f"http://{ip}", timeout=3)
    print(f"--- HTTP HEADERS ---")
    for k, v in resp.headers.items():
        print(f"{k}: {v}")
    print(f"\n--- HTML CONTENT ---")
    print(resp.text)
except Exception as e:
    print(e)
