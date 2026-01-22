import argparse
import time
from pythonosc import udp_client

# CONFIG
WING_IP = "192.168.1.11"
WING_PORT = 2223

def test_db(channel, db_value, ip, port):
    """
    Sends a float dB value to /ch/{channel}/fdr
    """
    client = udp_client.SimpleUDPClient(ip, port)
    address = f"/ch/{channel}/fdr"
    
    print(f"Sending {db_value} dB to {address}...")
    client.send_message(address, float(db_value))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Wing Mixer dB Control")
    parser.add_argument("--ch", type=int, default=1, help="Channel number (1-40)")
    parser.add_argument("--db", type=float, default=-40.0, help="dB value (-90.0 to +10.0)")
    parser.add_argument("--sweep", action="store_true", help="Sweep from -90dB to +10dB")
    
    args = parser.parse_args()
    
    if args.sweep:
        print("Starting dB Sweep (-90 to +10)...")
        # Sweep logic
        for i in range(-90, 11, 2):
            test_db(args.ch, float(i), WING_IP, WING_PORT)
            time.sleep(0.05)
        print("Sweep Done.")
    else:
        test_db(args.ch, args.db, WING_IP, WING_PORT)
