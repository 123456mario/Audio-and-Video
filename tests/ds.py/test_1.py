import time
from pythonosc import udp_client, osc_message_builder
import threading

WING_IP = "192.168.1.11"  # Wing IP
WING_PORT = 2223  # UDP 포트

def send_osc_command(address: str, value=None, arg_type='f'):
    client = udp_client.SimpleUDPClient(WING_IP, WING_PORT)
    msg = osc_message_builder.OscMessageBuilder(address=address)
    if value is not None:
        msg.add_arg(value, arg_type=arg_type)
    try:
        client.send(msg.build())
        print(f"[SUCCESS] Sent: {address} = {value}")
        return True
    except Exception as e:
        print(f"[ERROR] Send failed for {address}: {e}")
        return False

def heartbeat_loop():
    """Heartbeat (/xremote) 8초 간격 백그라운드 루프"""
    while True:
        send_osc_command("/xremote")
        time.sleep(8)

# Heartbeat 시작
print("[INIT] Starting heartbeat thread...")
threading.Thread(target=heartbeat_loop, daemon=True).start()

# 통신 테스트: Channel 1~8 뮤트 토글 (ON → OFF → ON)
print("[TEST] Waiting 2s for heartbeat...")
time.sleep(2)

for ch in range(1, 9):  # Channel 1~8
    ch_str = f"{ch:02d}"  # 01, 02, ... 08
    address = f"/ch/{ch_str}/mix/on"
    
    # Mute ON (0)
    print(f"[TEST] Channel {ch} Mute ON...")
    send_osc_command(address, 0)
    time.sleep(1)  # 1초 대기
    
    # Mute OFF (1)
    print(f"[TEST] Channel {ch} Mute OFF...")
    send_osc_command(address, 1)
    time.sleep(1)  # 1초 대기

print("[TEST] All channels mute test complete. Check Wing console for each channel mute toggle.")
print("[TEST] Running for 20s (heartbeat continues)...")
time.sleep(20)

print("[DONE] Test complete.")
