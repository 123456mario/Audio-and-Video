import socket
import time

XILICA_IP = "192.168.1.20"
XILICA_PORT = 10007

# Based on what we RECEIVED from Xilica: "set ch0m" and "set ch1m"
commands = [
    "set ch1m",  # Maybe this means ON?
    "set ch0m",  # Maybe this means OFF?
    "set ch1m 1",
    "set ch1m \"1\"", # Quoted
    "set ch1m \"true\"", # Quoted
]

print(f"🚀 Xilica Pattern Match Test ({XILICA_IP}:{XILICA_PORT})")

for cmd in commands:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((XILICA_IP, XILICA_PORT))
        
        full_cmd = f"{cmd}\r\n"
        print(f"👉 Sending: {full_cmd.strip()}")
        sock.send(full_cmd.encode())
        time.sleep(2) # Visual check
        sock.close()
    except Exception as e:
        print(f"❌ Error sending '{cmd}': {e}")
        time.sleep(1)

print("✅ Test Complete.")
