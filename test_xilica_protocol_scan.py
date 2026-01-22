import socket
import time

XILICA_IP = "192.168.1.20"
XILICA_PORT = 10007

formats = [
    "1", 
    "0", 
    "true", 
    "false", 
    "True", 
    "False", 
    "TRUE", 
    "FALSE", 
    "on", 
    "off",
    "On",
    "Off"
]

print(f"🚀 Xilica Direct Connection Test ({XILICA_IP}:{XILICA_PORT})")
print("Trying various Mute formats. Watch the screen!")

formats = [
    "1", "0", 
    "true", "false", 
    "True", "False", 
    "TRUE", "FALSE", 
    "on", "off",
    "On", "Off"
]

print(f"🚀 Xilica Direct Connection Test ({XILICA_IP}:{XILICA_PORT})")
print("Trying various Mute formats. Watch the screen!")

for fmt in formats:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((XILICA_IP, XILICA_PORT))
        
        cmd = f"set ch1m {fmt}\r\n"
        print(f"👉 Sending: {cmd.strip()}")
        sock.send(cmd.encode())
        time.sleep(1.5) # Wait for visual confirmation
        sock.close()
    except Exception as e:
        print(f"❌ Error sending '{fmt}': {e}")
        time.sleep(1)

print("✅ Test Complete.")
