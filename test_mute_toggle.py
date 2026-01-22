from pythonosc import udp_client
import time

IP = "127.0.0.1"
PORT = 50000
client = udp_client.SimpleUDPClient(IP, PORT)

print("👀 뮤트 버튼만 다시 테스트합니다...")
for i in range(3):
    print(f"[{i+1}/3] Mute ON (빨간불/켜짐)")
    client.send_message("/ch/01/mute", 1)
    time.sleep(1.5)
    
    print(f"[{i+1}/3] Mute OFF (꺼짐)")
    client.send_message("/ch/01/mute", 0)
    time.sleep(1.5)

print("완료!")
