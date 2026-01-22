from pythonosc import udp_client
import time

WING_IP = "192.168.1.11"
WING_PORT = 2223

client = udp_client.SimpleUDPClient(WING_IP, WING_PORT)

print(f"🚀 Starting Mute Test on {WING_IP}:{WING_PORT}")

def send_mute(ch, state):
    print(f"--- Channel {ch} MUTE {state} ---")
    
    val_int = 1 if state else 0
    val_inv = 0 if state else 1
    
    # SHOTGUN PATHS
    paths = [
        f"/ch/{ch}/mute",
        f"/ch/{ch:02d}/mute",
        f"/ch/{ch}/mix/on",
        f"/ch/{ch:02d}/mix/on"
    ]
    
    for p in paths:
        # Mix/On logic might be inverted on some firmwares? 
        # Usually 1=Mute, 0=Unmute for /mute
        # Usually 0=Off(Muted), 1=On(Unmuted) for /mix/on
        
        val = val_int
        if "mix/on" in p: val = val_inv
            
        print(f"  -> {p} {val}")
        client.send_message(p, val)

# Cycle Ch 1-8
for i in range(1, 9):
    # MUTE ON
    send_mute(i, True)
    time.sleep(0.5)
    
    # MUTE OFF
    # send_mute(i, False)
    # time.sleep(0.2)

print("✅ Done sending mutes.")
