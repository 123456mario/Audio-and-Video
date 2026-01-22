from pythonosc import udp_client
import time

WING_IP = "192.168.1.11"
WING_PORT = 2223

def run_test():
    client = udp_client.SimpleUDPClient(WING_IP, WING_PORT)
    print(f"DIRECT CONNECT: {WING_IP}:{WING_PORT}")

    print("\n--- MAIN 1 UNMUTE TEST ---")

    print("Unmuting Main 1...")
    client.send_message("/main/1/mute", 0)  # Mute OFF (0)
    
    # Optional: Set volume to 0dB
    client.send_message("/main/1/fdr", "0")
    
    print("\n✅ Sent Unmute to Main 1. Did it clear?")

if __name__ == "__main__":
    run_test()
