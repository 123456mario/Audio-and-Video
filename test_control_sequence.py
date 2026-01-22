import socket
import time

BRIDGE_IP = "192.168.1.50"
BRIDGE_PORT = 10001

def send_cmd(sock, cmd):
    print(f"Sending: {cmd}")
    sock.sendall(f"{cmd}\r\n".encode())
    time.sleep(0.5) # Wait for effect

def test_channel(sock, ch_idx):
    print(f"\n--- Testing Channel {ch_idx} ---")
    
    # Mute Test
    # Key mapping logic from bridge:
    # Ch1: ch1m
    # Ch2-8: {i}chm (e.g., 2chm)
    if ch_idx == 1:
        mute_key = "ch1m"
        vol_key = "ch1vol"
    else:
        mute_key = f"{ch_idx}chm"
        vol_key = f"ch{ch_idx}v"

    # Mute ON
    send_cmd(sock, f"set {mute_key} 1")
    time.sleep(0.5)
    # Mute OFF
    send_cmd(sock, f"set {mute_key} 0")
    
    # Volume Test (Fader Move)
    # -40dB -> -10dB -> -40dB
    print(f"Moving Fader {ch_idx}...")
    send_cmd(sock, f"set {vol_key} -40")
    time.sleep(0.2)
    send_cmd(sock, f"set {vol_key} -30")
    time.sleep(0.2)
    send_cmd(sock, f"set {vol_key} -20")
    time.sleep(0.2)
    send_cmd(sock, f"set {vol_key} -10") # Peak
    time.sleep(0.5)
    send_cmd(sock, f"set {vol_key} -20")
    time.sleep(0.2)
    send_cmd(sock, f"set {vol_key} -30")
    time.sleep(0.2)
    send_cmd(sock, f"set {vol_key} -40")

def test_main(sock):
    print(f"\n--- Testing Main Mix ---")
    # Mute Test
    # Key: MAIN_MUTE / MAIN_VOL
    send_cmd(sock, "SET MAIN_MUTE 1") # Mute
    time.sleep(0.5)
    send_cmd(sock, "SET MAIN_MUTE 0") # Unmute
    
    # Volume Test
    print("Moving Main Fader...")
    send_cmd(sock, "SET MAIN_VOL -40")
    time.sleep(0.2)
    send_cmd(sock, "SET MAIN_VOL -20")
    time.sleep(0.5)
    send_cmd(sock, "SET MAIN_VOL -40")

def main():
    print(f"Connecting to Bridge at {BRIDGE_IP}:{BRIDGE_PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((BRIDGE_IP, BRIDGE_PORT))
            print("Connected!")
            
            # Test Channels 1-8
            for i in range(1, 9):
                test_channel(s, i)
                time.sleep(0.5)
            
            # Test Main
            test_main(s)
            
            print("\n--- Test Sequence Complete ---")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
