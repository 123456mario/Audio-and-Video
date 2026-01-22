# Behringer Wing OSC → Xilica TCP 브릿지 (if __name__ 제거 버전)

import socket
import threading
import time
from pythonosc import udp_client, dispatcher, osc_server

WING_IP = "192.168.1.11"
WING_PORT = 2223
TCP_PORT = 10000
XILICA_IP = "192.168.1.20"
XILICA_PORT = 10007

# CH1 키: 뮤트 "ch1m" (on), "ch0m" (off), "ch1vol" (vol)
SELECTED_CONTROLS = {
    "ch1m": "/ch/01/mute",  # MUTE on: "set ch1m" (val = 1 가정)
    "ch0m": "/ch/01/mute",  # MUTE off: "set ch0m" (val = 0 가정)
    "ch1vol": "/ch/01/fader",  # VOL: "set ch1vol -10.0"
    # 다른 채널 확장 시 추가
}

current_states = {key: None for key in SELECTED_CONTROLS}

def db_to_osc(db):
    if db <= -80: return 0.0
    return min(1.0, (db + 80) / 90)

def osc_to_db(osc_val):
    if osc_val == 0: return -80.0
    return osc_val * 90 - 80

def osc_handler(address, value):
    print(f"🎵 OSC 수신: {address} = {value}")
    for key, path in SELECTED_CONTROLS.items():
        if address == path:
            if "vol" in key:
                value = osc_to_db(value)
            current_states[key] = value
            push_to_xilica(key, value)

def push_to_xilica(key, value):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((XILICA_IP, XILICA_PORT))
        data = f"{key} {value}\r\n"
        sock.send(data.encode())
        sock.close()
        print(f"📤 Xilica로 푸시: {key} = {value}")
    except Exception as e:
        print(f"❌ Xilica 푸시 오류: {e}")

disp = dispatcher.Dispatcher()
for path in SELECTED_CONTROLS.values():
    disp.map(path, osc_handler)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 50000), disp)
threading.Thread(target=server.serve_forever).start()

def subscribe_renew():
    while True:
        for path in SELECTED_CONTROLS.values():
            try:
                osc_client.send_message(path + "s~renew", [8])
                print(f"📡 Wing 구독 신청: {path}")
            except Exception as e:
                print(f"⚠️ Wing 구독 오류 무시: {e} (장비 연결 확인)")
        time.sleep(8)

threading.Thread(target=subscribe_renew).start()

def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", TCP_PORT))
    sock.listen(5)
    print(f"✅ TCP 서버 시작: 포트 {TCP_PORT}에서 Xilica 데이터 대기...")
    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024).decode('utf-8', errors='ignore').strip()
        if data:
            print(f"📥 수신된 데이터: {data} (from {addr})")
            parts = data.split()
            if len(parts) >= 2 and parts[0].lower() == "set":
                if len(parts) == 2:  # VALUE 생략 (뮤트 토글)
                    key = parts[1].lower()
                    val = 1 if key == "ch1m" else 0  # ch1m = on (1), ch0m = off (0)
                    print(f"📋 VALUE 생략 처리: {key} = {val} (토글 가정)")
                else:  # VALUE 있음 (볼륨)
                    key = parts[1].lower()
                    val = float(parts[2]) if "vol" in key else int(parts[2])
                if key in SELECTED_CONTROLS:
                    current_states[key] = val
                    print(f"✅ 상태 업데이트: {key} = {val} (현재 상태: {current_states[key]})")
                    # 필요 시 Xilica로 푸시 (테스트 중이라면 주석)
                    # push_to_xilica(key, val)
                    conn.send(b"OK\r\n")
                else:
                    print(f"❌ 알 수 없는 키: {key} (유효 키: {list(SELECTED_CONTROLS.keys())})")
                    conn.send(b"ERROR\r\n")
            else:
                print(f"❌ 데이터 형식 오류: 최소 'set KEY [VALUE]' 필요 (parts: {parts})")
                conn.send(b"ERROR\r\n")
        else:
            print(f"⚠️ 빈 데이터 수신")
        conn.close()

threading.Thread(target=tcp_server).start()

print("🚀 브릿지 실행: Wing OSC → Xilica TCP (if __name__ 제거 버전, Ctrl+C 종료)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 브릿지 종료")
