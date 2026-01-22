from pythonosc import udp_client
import time

IP = "192.168.1.11"
PORT = 2223

client = udp_client.SimpleUDPClient(IP, PORT)

print(f"Sending to {IP}:{PORT}...")

# Test 1: Mute Channel 5 (Mute ON)
print("1. Muting CH 5...")
client.send_message("/ch/5/mute", 1)
client.send_message("/ch/5/mix/on", 0)
time.sleep(1)

# Test 2: Set Volume CH 5 to 75% (Normalized)
print("2. Setting CH 5 Volume to 75% (Normalized 0.75)...")
client.send_message("/ch/5/fdr", 0.75)
client.send_message("/ch/5/mix/fader", 0.75)

print("Done. Check Mixer.")
