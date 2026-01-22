from pythonosc import udp_client
import time

# Bridge OSC Port
IP = "127.0.0.1"
PORT = 50000

client = udp_client.SimpleUDPClient(IP, PORT)

print("👀 Xilica 화면을 보세요! 페이더와 뮤트가 움직입니다.")
print("--- 데모 시작 ---")

try:
    # 1. Mute Toggle
    print("Toggle Mute...")
    client.send_message("/ch/01/mute", 1) # Mute
    time.sleep(1)
    client.send_message("/ch/01/mute", 0) # Unmute
    time.sleep(1)

    # 2. Volume Ramp Up (-60dB to +10dB)
    # Wing Value: 0.0625 to 1.0
    print("Volume Up...")
    for i in range(0, 101, 5):
        val = i / 100.0
        client.send_message("/ch/01/fader", val)
        time.sleep(0.05)

    time.sleep(1)

    # 3. Volume Ramp Down
    print("Volume Down...")
    for i in range(100, -1, -5):
        val = i / 100.0
        client.send_message("/ch/01/fader", val)
        time.sleep(0.05)
        
    # 4. Blink Mute
    print("Blinking Mute...")
    for _ in range(3):
        client.send_message("/ch/01/mute", 1)
        time.sleep(0.3)
        client.send_message("/ch/01/mute", 0)
        time.sleep(0.3)

    print("--- 데모 완료 ---")

except KeyboardInterrupt:
    pass
