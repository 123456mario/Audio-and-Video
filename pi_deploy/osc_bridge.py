import socket
import threading
import time
import logging
from pythonosc import udp_client, dispatcher, osc_server
import requests
from requests.auth import HTTPDigestAuth

# logger 정의
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# 설정
WING_IP = "127.0.0.1" # Virtual Wing
WING_PORT = 2223
TCP_PORT = 10001
XILICA_IP = "192.168.1.20" # Real Xilica
XILICA_PORT = 10007 # Bridge -> Xilica 송신 포

# PTZ Camera Config
CAM1_IP = "192.168.1.30"
CAM2_IP = "192.168.1.31"
CAM_USER = "admin"
CAM_PASS = "1234"

# PTZ Directions
PTZ_DIRECTIONS = {
    "RIGHT": "%23PTS9950",
    "LEFT": "%23PTS0150",
    "UP": "%23PTS5099",
    "DOWN": "%23PTS5001",
    "STOP": "%23PTS5050",
    "HOME": "%23APC7FFF7FFF",
    "ZOOMIN": "%23Z80",
    "ZOOMOUT": "%23Z20",
    "ZOOMSTOP": "%23Z50"
}

# OSC 클라이언트 (Wing으로 전송용)
osc_client = udp_client.SimpleUDPClient(WING_IP, WING_PORT)

# --- CONFIGURATION: Wing OSC Mapping ---
# 채널 개수 설정 (필요시 변경)
WING_CHANNEL_COUNT = 8

# Wing OSC 주소 포맷
OSC_ADDR_CH_FADER_FMT = "/ch/{:02d}/fader"
OSC_ADDR_CH_MUTE_FMT = "/ch/{:02d}/mute"
OSC_ADDR_MAIN_FADER = "/main/st/mix/fader"
OSC_ADDR_MAIN_MUTE = "/main/st/mix/on" # Wing: 1=On(Sound), 0=Off(Mute)

# Xilica Key 포맷 (Lua 스크립트와 일치)
# Lua: "CH"..i.."_VOL", "CH"..i.."_MUTE", "MAIN_VOL", "MAIN_MUTE"
# Python Bridge (Internal Keys match normalized Lua output or simple keys)
# 여기서는 소문자로 내부 키를 관리함.
KEY_CH_VOL_FMT = "ch{}vol"
KEY_CH_MUTE_FMT = "ch{}mute"
KEY_MAIN_VOL = "mainvol"
KEY_MAIN_MUTE = "mainmute"

# 매핑 정의 (KEY <-> OSC Address)
CONTROL_MAP = {}

# 1. 일반 채널 매핑 (1 ~ N)
for i in range(1, WING_CHANNEL_COUNT + 1):
    # ch1vol -> /ch/01/fader
    key_vol = KEY_CH_VOL_FMT.format(i)
    osc_vol = OSC_ADDR_CH_FADER_FMT.format(i)
    CONTROL_MAP[key_vol] = osc_vol
    
    # ch1mute -> /ch/01/mute
    key_mute = KEY_CH_MUTE_FMT.format(i)
    osc_mute = OSC_ADDR_CH_MUTE_FMT.format(i)
    CONTROL_MAP[key_mute] = osc_mute

# 2. 메인 L/R 매핑
CONTROL_MAP[KEY_MAIN_VOL] = OSC_ADDR_MAIN_FADER
CONTROL_MAP[KEY_MAIN_MUTE] = OSC_ADDR_MAIN_MUTE

# 역방향 매핑 (OSC -> KEY)
OSC_TO_KEY = {v: k for k, v in CONTROL_MAP.items()}

# 현재 상태 저장 (루프 방지용)
current_states = {key: None for key in CONTROL_MAP}

# Behringer Wing/X32 Fader Curve Points
# (dB, OSC Float)
FADER_POINTS = [
    (-90.0, 0.0),
    (-60.0, 0.0625),
    (-30.0, 0.25),
    (-10.0, 0.5),
    (0.0, 0.75),
    (5.0, 0.875), # Approx
    (10.0, 1.0)
]

def db_to_osc(db):
    """Xilica dB (-90 ~ +10) -> Wing Float (0.0 ~ 1.0) using Piecewise Linear Interpolation"""
    if db <= -90.0: return 0.0
    if db >= 10.0: return 1.0
    
    # 구간 찾기
    for i in range(len(FADER_POINTS) - 1):
        db1, val1 = FADER_POINTS[i]
        db2, val2 = FADER_POINTS[i+1]
        
        if db1 <= db <= db2:
            # 선형 보간
            ratio = (db - db1) / (db2 - db1)
            return val1 + ratio * (val2 - val1)
            
    return 0.0 # Should not happen

def osc_to_db(osc_val):
    """Wing Float (0.0 ~ 1.0) -> Xilica dB using Piecewise Linear Interpolation"""
    if osc_val <= 0.0: return -90.0
    if osc_val >= 1.0: return 10.0
    
    for i in range(len(FADER_POINTS) - 1):
        db1, val1 = FADER_POINTS[i]
        db2, val2 = FADER_POINTS[i+1]
        
        if val1 <= osc_val <= val2:
            ratio = (osc_val - val1) / (val2 - val1)
            return db1 + ratio * (db2 - db1)
            
    return -90.0

def send_osc_to_wing(address, value):
    """Wing으로 OSC 전송"""
    osc_client.send_message(address, value)
    logger.info(f"📤 Wing으로 전송: {address} = {value}")

def push_to_xilica(key, value):
    """Xilica로 TCP 명령 전송"""
    try:
        final_val = value
        # Mute 처리: 키가 Mute 관련 키인지 확인
        # 단순히 "MUTE" 문자열 포함 여부보다는 설정된 포맷이나 명시적 키 확인 권장
        # 여기서는 편의상 "mute"가 포함되었거나 legacy "m"으로 끝나는지 확인
        is_mute_key = "mute" in key.lower() or key.endswith("m")
        
        if is_mute_key:
            if value == 1: final_val = "TRUE"
            elif value == 0: final_val = "FALSE"
            
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1) # 타임아웃 추가
        sock.connect((XILICA_IP, XILICA_PORT))
        # 포맷: "SET KEY VALUE\r" (CR only per API docs/test)
        data = f"SET {key} {final_val}\r"
        sock.send(data.encode())
        sock.close()
        logger.info(f"📤 Xilica로 푸시: {key} = {final_val}")
    except Exception as e:
        logger.error(f"❌ Xilica 푸시 오류: {e}")

def osc_handler(address, *args):
    """Wing에서 오는 OSC 메시지 처리"""
    if not args: return
    value = args[0]
    
    logger.info(f"🎵 OSC 수신: {address} = {value}")
    
    if address in OSC_TO_KEY:
        key = OSC_TO_KEY[address]
        
        # 값 변환
        xilica_val = value
        
        # 키 타입 판별
        is_main_mute = (key == KEY_MAIN_MUTE)
        is_mute_general = "mute" in key.lower() or key.endswith("m")
        is_vol_general = "vol" in key.lower()
        
        if is_vol_general:
            xilica_val = osc_to_db(value)
        elif is_mute_general: 
             # Main Mute 반전 처리 (Wing /on -> Xilica /mute)
            if is_main_mute: 
                xilica_val = 0 if value == 1 else 1 # On=1 -> Mute=0
            else:
                xilica_val = int(value)
        
        # 상태 확인 (중복 전송 방지)
        stored = current_states.get(key)
        
        need_update = True
        if stored is not None:
            if isinstance(xilica_val, float):
                if abs(stored - xilica_val) < 0.1: need_update = False
            else:
                if stored == xilica_val: need_update = False
        
        if need_update:
            current_states[key] = xilica_val
            push_to_xilica(key, xilica_val)

# 레거시 명령어 매핑 (값 없는 명령어 지원용)
KEY_CH1_MUTE = KEY_CH_MUTE_FMT.format(1)
LEGACY_MAP = {
    "CH0M": (KEY_CH1_MUTE, 0), # CH1 Mute Off
    "CH1M": (KEY_CH1_MUTE, 1), # CH1 Mute On
}

def control_ptz(cam_ip, command):
    """PTZ 카메라 제어 요청"""
    url = f"http://{cam_ip}/cgi-bin/aw_ptz?cmd={command}&res=1"
    try:
        response = requests.get(url, auth=HTTPDigestAuth(CAM_USER, CAM_PASS), timeout=2)
        if response.status_code == 200:
            logger.info(f"🎥 PTZ Success: {cam_ip} -> {command}")
        else:
            logger.error(f"❌ PTZ Fail: {cam_ip} {response.status_code}")
    except Exception as e:
        logger.error(f"❌ PTZ Request Error: {e}")

def handle_client(conn, addr):
    """개별 클라이언트 연결을 처리하는 함수 (스레드)"""
    print(f"DEBUG: Connection accepted from {addr}", flush=True)
    conn.settimeout(None) 
    
    with conn: 
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"DEBUG: Connection closed by {addr}", flush=True)
                    break
                
                decoded_data = data.decode('utf-8', errors='ignore').strip()
                print(f"DEBUG: Received raw data from {addr}: {decoded_data}", flush=True)
                
                if not decoded_data:
                    continue
                
                lines = decoded_data.splitlines()
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    parts = line.split()
                    cmd_type = parts[0].upper()
                    
                    # 1. SET Command (Audio)
                    if cmd_type == "SET" and len(parts) >= 2:
                        raw_key = parts[1].upper() # Incoming is usually UPPER from some systems, or user typed
                        
                        matched_target_key = None
                        matched_target_val = None
                        
                        # 1. 레거시
                        if len(parts) == 2:
                            if raw_key in LEGACY_MAP:
                                matched_target_key, matched_target_val = LEGACY_MAP[raw_key]
                            else:
                                print(f"WARNING: Unknown key {raw_key}", flush=True)
                                conn.send(b"ERROR\r\n")
                                continue
                        # 2. 일반
                        else:
                            val_str = parts[2]
                            # Case-insensitive matching
                            # CONTROL_MAP keys are lowercase now (ch1vol)
                            # raw_key might be CH1VOL
                            
                            # Exact match loop
                            for k in CONTROL_MAP:
                                if k.upper() == raw_key:
                                    matched_target_key = k
                                    break
                            
                            # Fuzzy match loop (ignore underscores)
                            if not matched_target_key:
                                normalized_input = raw_key.replace("_", "")
                                for k in CONTROL_MAP:
                                    if k.upper().replace("_", "") == normalized_input:
                                        matched_target_key = k
                                        break
                                        
                            if matched_target_key:
                                try:
                                    matched_target_val = float(val_str)
                                except:
                                    print(f"ERROR: Float parse fail {val_str}", flush=True)
                                    conn.send(b"ERROR\r\n")
                                    continue
                        
                        if matched_target_key:
                            osc_addr = CONTROL_MAP[matched_target_key]
                            osc_val = 0.0
                            
                            # 키 타입 판별 (Upper removed, using matched_target_key)
                            is_main_mute = (matched_target_key == KEY_MAIN_MUTE)
                            is_mute = "mute" in matched_target_key.lower() or matched_target_key.endswith("m")
                            is_vol = "vol" in matched_target_key.lower()
                            
                            if is_vol:
                                osc_val = db_to_osc(float(matched_target_val))
                                current_states[matched_target_key] = float(matched_target_val)
                                
                            elif is_mute:
                                # MUTE Logic Check:
                                v = int(matched_target_val)
                                if is_main_mute:
                                    osc_val = 0 if v == 1 else 1
                                else:
                                    osc_val = v
                                current_states[matched_target_key] = v
                            
                            send_osc_to_wing(osc_addr, osc_val)
                            conn.send(b"OK\r\n")
                        else:
                            conn.send(b"ERROR\r\n")

                    # 2. CAM Command (PTZ)
                    # Format: CAM1 UP ON / CAM1 UP OFF
                    elif cmd_type.startswith("CAM") and len(parts) >= 3:
                        cam_id = cmd_type # CAM1 or CAM2
                        direction = parts[1].upper()
                        state = parts[2].upper()
                        
                        # Determine Target IP
                        target_ip = None
                        if cam_id == "CAM1": target_ip = CAM1_IP
                        elif cam_id == "CAM2": target_ip = CAM2_IP
                        
                        if target_ip:
                            cgi_cmd = None
                            
                            if state == "ON":
                                if direction in PTZ_DIRECTIONS:
                                    cgi_cmd = PTZ_DIRECTIONS[direction]
                            
                            elif state == "OFF":
                                # Stop Logic
                                if direction in ["ZOOMIN", "ZOOMOUT"]:
                                    cgi_cmd = PTZ_DIRECTIONS["ZOOMSTOP"]
                                elif direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                    cgi_cmd = PTZ_DIRECTIONS["STOP"]
                                # HOME is one-shot, ignore OFF
                            
                            if cgi_cmd:
                                threading.Thread(target=control_ptz, args=(target_ip, cgi_cmd), daemon=True).start()
                                conn.send(b"OK\r\n")
                            else:
                                # Invalid direction or ignore OFF for HOME
                                conn.send(b"OK\r\n")
                        else:
                            print(f"WARNING: Unknown Camera {cam_id}", flush=True)
                            conn.send(b"ERR\r\n")

                    elif cmd_type == "STOP": # Global Stop
                         threading.Thread(target=control_ptz, args=(CAM1_IP, PTZ_DIRECTIONS["STOP"]), daemon=True).start()
                         threading.Thread(target=control_ptz, args=(CAM2_IP, PTZ_DIRECTIONS["STOP"]), daemon=True).start()
                         conn.send(b"OK\r\n")

                    else:
                        print(f"WARNING: Bad format {line}", flush=True)
            except Exception as e:
                print(f"ERROR: Client loop exception {e}", flush=True)
                break

def tcp_server():
    """Xilica에서 오는 TCP 데이터 수신 (Multi-threaded)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("192.168.1.9", TCP_PORT))
    except Exception as e:
        logger.error(f"TCP Bind Error: {e}")
        return

    sock.listen(5)
    logger.info(f"✅ TCP 서버 시작: {TCP_PORT} (Multi-threaded)")
    
    while True:
        try:
            conn, addr = sock.accept()
            # 별도 스레드로 처리하여 블로킹 방지
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
        except Exception as e:
            logger.error(f"TCP Accept Error: {e}")
            time.sleep(1)

def keep_alive_sender():
    """Wing에 주기적으로 /xremote 전송 (구독 갱신)"""
    logger.info("Keep-alive 스레드 시작")
    while True:
        try:
            # Behringer 콘솔은 주기적으로 /xremote 전송해야 미터/데이터 갱신 받을 수 있음
            # Wing의 경우 다를 수 있으나 보통 필요함
            osc_client.send_message("/xremote", [])
            # logger.debug("Sent /xremote")
            time.sleep(9) 
        except Exception as e:
            logger.error(f"Keep-alive 오류: {e}")
            time.sleep(5)

# 디스패처 설정
disp = dispatcher.Dispatcher()
# 매핑된 모든 주소 구독
for path in CONTROL_MAP.values():
    disp.map(path, osc_handler)
# 모든 메시지 디버깅용 (필요시 활성화)
# disp.set_default_handler(logger.info)

def main():
    # OSC 서버 시작 (Wing -> Bridge)
    # 포트는 임의로 50000 (Wing에서 이 포트로 쏴줘야 함)
    # 실제로는 Wing 연결 시 자신의 수신 포트를 알려주거나, Wing 설정에서 Bridge IP:50000을 타겟으로 잡아야 함.
    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 50000), disp)
    logger.info("🎵 OSC 서버 시작: 포트 50000")
    
    t_osc = threading.Thread(target=server.serve_forever, daemon=True)
    t_osc.start()
    
    t_tcp = threading.Thread(target=tcp_server, daemon=True)
    t_tcp.start()

    t_keep = threading.Thread(target=keep_alive_sender, daemon=True)
    t_keep.start()

    logger.info("브릿지 실행 중. 종료하려면 Ctrl+C")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("종료 중...")

if __name__ == "__main__":
    main()