from pythonosc import udp_client
import time

IP = "127.0.0.1"
PORT = 50000
client = udp_client.SimpleUDPClient(IP, PORT)

print("🚀 최종 테스트 시작: 뮤트 4회 + 볼륨 2회 왕복")
time.sleep(1)

# 1. Mute Toggle 4 times
print("\n--- 1. 뮤트 테스트 (4회 깜빡임) ---")
for i in range(4):
    print(f"[{i+1}/4] Mute ON (빨간불)")
    client.send_message("/ch/01/mute", 1)
    time.sleep(0.8)
    
    print(f"[{i+1}/4] Mute OFF (꺼짐)")
    client.send_message("/ch/01/mute", 0)
    time.sleep(0.8)

time.sleep(1)

# 2. Volume Ramp 2 times
print("\n--- 2. 볼륨 테스트 (2회 왕복) ---")
for cycle in range(2):
    print(f"[{cycle+1}/2] 볼륨 올리기 📈")
    for i in range(0, 101, 5): # 0% ~ 100%
        val = i / 100.0
        client.send_message("/ch/01/fader", val)
        time.sleep(0.04)
    
    time.sleep(0.5)
    
    print(f"[{cycle+1}/2] 볼륨 내리기 📉")
    for i in range(100, -1, -5): # 100% ~ 0%
        val = i / 100.0
        client.send_message("/ch/01/fader", val)
        time.sleep(0.04)
    
    time.sleep(1)

print("\n✅ 모든 테스트 완료! 수고하셨습니다.")
