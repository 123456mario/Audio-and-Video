import socket
import time

TARGET_IP = "192.168.1.60"
PORT = 19999

# The raw HTTP request string Xilica needs to send
# Note: \r\n line endings are standard for HTTP
RAW_PAYLOAD = (
    "GET /unico/v1/node/power HTTP/1.1\r\n"
    "Host: 192.168.1.60:19999\r\n"
    "ip: 127.0.0.1\r\n"
    "port: 80\r\n"
    "protocol: http\r\n"
    "Connection: close\r\n"
    "\r\n"
)

print(f"📡 Sending Raw TCP Payload to {TARGET_IP}:{PORT}...")
print(f"---\n{RAW_PAYLOAD}---")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    s.connect((TARGET_IP, PORT))
    
    s.sendall(RAW_PAYLOAD.encode('utf-8'))
    
    response = b""
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        response += chunk
        
    s.close()
    
    print("\n✅ RESPONSE RECEIVED:")
    print(response.decode('utf-8', errors='replace'))
    
except Exception as e:
    print(f"❌ Failed: {e}")
