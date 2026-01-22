import socket
import time

XILICA_IP = "192.168.1.20"
XILICA_PORT = 10007

print(f"🚀 Xilica Uppercase Boolean Test ({XILICA_IP}:{XILICA_PORT})")
print("Trying 'TRUE' / 'FALSE' with CR (\\r) termination.")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((XILICA_IP, XILICA_PORT))
    
    for i in range(5):
        print(f"\n--- Cycle {i+1}/5 ---")
        
        # Test 1: TRUE with \r
        msg = "SET ch1m TRUE\r"
        print(f"👉 Sending: {msg.strip()} (CR only)")
        sock.send(msg.encode())
        time.sleep(2)
        
        # Test 2: FALSE with \r
        msg = "SET ch1m FALSE\r"
        print(f"👉 Sending: {msg.strip()} (CR only)")
        sock.send(msg.encode())
        time.sleep(2)
        
    sock.close()
    print("✅ Test Complete.")

except Exception as e:
    print(f"❌ Error: {e}")
