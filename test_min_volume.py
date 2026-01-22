import argparse
import time
from pythonosc import udp_client

# CONFIG
WING_IP = "192.168.1.11"
WING_PORT = 2223

def test_min_vol(ip, port):
    client = udp_client.SimpleUDPClient(ip, port)
    
    # Candidate Addresses to test "Silence"
    candidates = [
        "/ch/1/fdr",         # Used in osc_bridge.py currently
        "/ch/1/mix_fader",   # Found in osc_bridge_v2.py / mixer_type_wing.py
        "/ch/1/mix/fader",   # Standard X32
        "/ch/01/mix/fader",  # Zero-padded standard
    ]
    
    print(f"--- Sending LOWEST VALUE (-90.0 dB) to Channel 1 on {ip}:{port} ---")
    
    for addr in candidates:
        print(f"Trying {addr} ...")
        # Send twice to ensure it catches
        client.send_message(addr, -90.0)
        time.sleep(0.1)
        client.send_message(addr, -90.0)
        time.sleep(1.0) # Wait for user to observe
        
    print("--- Done. Did the fader drop to bottom? ---")

if __name__ == "__main__":
    test_min_vol(WING_IP, WING_PORT)
