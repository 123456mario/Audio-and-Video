from pythonosc import udp_client
import time

WING_IP = "192.168.1.11"
WING_PORT = 2223

client = udp_client.SimpleUDPClient(WING_IP, WING_PORT)

print(f"🚀 Starting Path Isolation Test on {WING_IP}:{WING_PORT}")
print("Check which channels Respond!")

def test_path(ch_custom, path_format, val, desc):
    path = path_format.format(ch_custom)
    print(f"👉 Ch {ch_custom}: Sending {path} ({desc})...")
    client.send_message(path, val)
    time.sleep(0.5)

# --- MUTE TESTS (1=Muted) ---
print("\n--- Testing MUTE/ON Paths ---")
test_path(1, "/ch/{}/mute", 1, "Standard Mute")
test_path(2, "/ch/{:02d}/mute", 1, "Padded Mute (02)")
test_path(3, "/ch/{}/mix/on", 0, "Mix On (0=Muted?)") 
test_path(4, "/ch/{:02d}/mix/on", 0, "Padded Mix On (0=Muted?)")

# --- FADER TESTS (Using -20dB = approx 0.7?) ---
# We use direct dB float just in case, but let's try normalized too?
# No, we established dB is needed. Sending -20.0
dB_VAL = -20.0

print(f"\n--- Testing FADER Paths with {dB_VAL} dB ---")
test_path(5, "/ch/{}/fdr", dB_VAL, "Standard Fdr")
test_path(6, "/ch/{:02d}/fdr", dB_VAL, "Padded Fdr (06)")
test_path(7, "/ch/{}/fader", dB_VAL, "Alias Fader")
test_path(8, "/ch/{:02d}/fader", dB_VAL, "Padded Alias Fader (08)")
test_path(9, "/ch/{}/mix/fader", dB_VAL, "Mix Fader")
test_path(10, "/ch/{:02d}/mix/fader", dB_VAL, "Padded Mix Fader (10)")

print("\n✅ Done. Please tell me which channels reacted!")
