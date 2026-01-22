import socket
import time

# Configuration
BRIDGE_IP = "127.0.0.1"
BRIDGE_PORT = 10021

def send_test_packet(universe, value, description):
    print(f"--- Sending: {description} ---")
    print(f"Target: Universe {universe} -> Value {value}")
    
    # Create binary packet: [Universe Byte] [Value Byte]
    packet = bytes([universe, value])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(packet, (BRIDGE_IP, BRIDGE_PORT))
        print(f"Sent: {packet.hex()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
    
    print("---------------------------------")
    time.sleep(1)

if __name__ == "__main__":
    print("Test Script Starting...")
    
    # Test Group A (Input 1 -> Univ 0 -> DMX 7,8)
    send_test_packet(0, 255, "Group A (Input 1 / Univ 0) ON")
    
    # Test Group B (Input 2 -> Univ 1 -> DMX 9,10)
    send_test_packet(1, 255, "Group B (Input 2 / Univ 1) ON")
    
    # Test Legacy/Odd (Input 3 -> Univ 2 -> DMX 7,8)
    send_test_packet(2, 128, "Group A Audit (Input 3 / Univ 2) HALF")
    
    # Test Unknown
    send_test_packet(5, 255, "Unknown Universe 5")
    
    print("Done.")
