from pythonosc import udp_client
import time

# Wing이 보낼 UDP 50000번으로 OSC 피드백 시뮬레이션
client = udp_client.SimpleUDPClient("127.0.0.1", 50000)  # 로컬 RPi 서버

print("Wing 피드백 시뮬레이터 시작 - 2초마다 MUTE/볼륨 변경")

count = 0
while True:
    count += 1
    
    if count % 2 == 0:
        # MUTE ON + 볼륨 -10dB
        client.send_message("/ch/01/mute", 1.0)
        client.send_message("/ch/01/fdr", -10.0)
        print("시뮬: MUTE ON, VOL -10dB")
    else:
        # MUTE OFF + 볼륨 5dB
        client.send_message("/ch/01/mute", 0.0)
        client.send_message("/ch/01/fdr", 5.0)
        print("시뮬: MUTE OFF, VOL 5dB")
    
    time.sleep(2)