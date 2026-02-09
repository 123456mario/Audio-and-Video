import socket
import threading
import time
import select
import logging
import struct
import re
from pythonosc import osc_message_builder

# --- CONFIGURATION ---
PI_LISTEN_PORT = 10025 
XILICA_IP = "192.168.1.20"
XILICA_FEEDBACK_PORT = 10007

WING_IP = "192.168.1.11"
WING_TARGET_PORT = 2223 
WING_LOCAL_BIND_PORT = 33901 

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("BridgeV5")

running = True

# --- CACHE FOR FEEDBACK LOOP PREVENTION ---
xilica_value_cache = {} 
cache_lock = threading.Lock()

# --- VOLUME MAP (0-10) ---
VOL_MAP = {
    0: -90.0, 1: -40.0, 2: -30.0, 3: -20.0, 4: -15.0, 
    5: -10.0, 6: -5.0, 7: 0.0, 8: 3.0, 9: 6.0, 10: 10.0
}

def map_step_to_db(step_val):
    try:
        idx = int(float(step_val))
        return VOL_MAP.get(idx, -90.0)
    except: return -90.0

# --- VOLUME MAPPING (Scale-Aware v5.5) ---
WING_MODE_CACHE = {} 
PREV_STEP_CACHE = {} 

def map_wing_to_step(val, key):
    global WING_MODE_CACHE, PREV_STEP_CACHE
    prev_step = PREV_STEP_CACHE.get(key, 0)
    prev_mode = WING_MODE_CACHE.get(key)
    
    # 1. Mode Lock: Negative or > 1.1 is definitively dB.
    if val < -0.1 or val > 1.1:
        if prev_mode != "db":
            logger.info(f"📡 {key}: Mode dB (val={val:.2f})")
            WING_MODE_CACHE[key] = "db"
    elif 0.05 < val < 0.95 and prev_mode is None:
        WING_MODE_CACHE[key] = "norm"

    mode = WING_MODE_CACHE.get(key, "norm")
    
    # 2. Logic Mapping
    step = 0
    if mode == "db":
        if val <= -88.0: step = 0
        elif val == 0.0:
            # Jump Guard: 0.0 in dB mode is Step 7 (0dB). 
            # But Wing sends 0.0 at bottom too.
            step = 0 if prev_step <= 3 else 7
        else:
            best_s = 0; min_d = float('inf')
            for s, d in VOL_MAP.items():
                diff = abs(d - val)
                if diff < min_d: min_d = diff; best_s = s
            step = best_s
    else:
        # Normalized Mode
        if val < 0.01: step = 0
        elif val >= 0.73: # 0dB region (~0.75)
             if val >= 0.95: step = 10
             elif val >= 0.88: step = 9
             elif val >= 0.81: step = 8
             else: step = 7
        else:
             if val >= 0.65: step = 6
             elif val >= 0.55: step = 5
             elif val >= 0.45: step = 4
             elif val >= 0.35: step = 3
             elif val >= 0.20: step = 2
             elif val >= 0.05: step = 1
             else: step = 0

    PREV_STEP_CACHE[key] = step
    return step

def normalize_key(key):
    k = str(key).lower()
    if any(x in k for x in ["main_vol", "mvol", "mv", "mainv"]): return "mv"
    if any(x in k for x in ["main_mute", "mmute", "mainm"]): return "mmute"
    match = re.search(r'(\d+)', k)
    if match:
        ch_num = str(int(match.group(1)))
        if "v" in k or "vol" in k: return f"{ch_num}chv"
        if "m" in k or "mute" in k: return f"{ch_num}chm"
    return k

# --- NETWORK ---
wing_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wing_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    wing_sock.bind(('0.0.0.0', WING_LOCAL_BIND_PORT))
    logger.info(f"✅ Wing Bound {WING_LOCAL_BIND_PORT}")
except Exception as e:
    logger.error(f"❌ Wing Bind: {e}")

xilica_sock = None

def connect_to_xilica():
    global xilica_sock
    while running:
        if xilica_sock is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((XILICA_IP, XILICA_FEEDBACK_PORT))
                logger.info(f"✅ Xilica Feedback Connected ({XILICA_IP}:{XILICA_FEEDBACK_PORT})")
                xilica_sock = s
            except: time.sleep(5)
        else: time.sleep(2)

def update_xilica_safely(key, value):
    norm_key = normalize_key(key)
    with cache_lock:
        if xilica_value_cache.get(norm_key) == str(value): return
        xilica_value_cache[norm_key] = str(value)
        # Lockout
        if time.time() - last_cmd_time.get(norm_key, 0) < 4.0: return 
    
    cmd = f"SET {norm_key} {value}\r\n" # Inclusive delimiter
    if xilica_sock:
        try:
            xilica_sock.sendall(cmd.encode())
            logger.info(f"🛡️ Safe Update: {cmd.strip()}")
        except: pass

# --- HANDLERS ---
def handle_control_client(conn):
    with conn:
        buffer = ""
        while running:
            try:
                data = conn.recv(1024)
                if not data: break
                buffer += data.decode(errors='ignore')
                while '\r' in buffer or '\n' in buffer:
                    line = ""
                    if '\r' in buffer: line, buffer = buffer.split('\r', 1)
                    elif '\n' in buffer: line, buffer = buffer.split('\n', 1)
                    process_control_cmd(line.strip())
            except: break

last_cmd_time = {}

def process_control_cmd(line):
    if not line: return
    logger.info(f"📥 RAW RECV: {line}")
    parts = line.split()
    if len(parts) < 3: return
    key, val = parts[1], parts[2]
    norm_key = normalize_key(key)
    
    with cache_lock:
        last_cmd_time[norm_key] = time.time()
        v_cln = val.replace(".0", "")
        if xilica_value_cache.get(norm_key) == v_cln: return
        xilica_value_cache[norm_key] = v_cln

    # Send to Wing
    ch = "main" if norm_key in ["mv", "mmute"] else re.search(r'(\d+)', norm_key).group(1)
    if "m" in norm_key:
        addr = "/main/1/mute" if ch == "main" else f"/ch/{ch}/mute"
        send_wing_osc(addr, 1 if (val == "1" or val.upper() == "TRUE") else 0)
    else:
        addr = "/main/1/fdr" if ch == "main" else f"/ch/{ch}/fdr"
        send_wing_osc(addr, f"{map_step_to_db(val):.1f}")

def send_wing_osc(addr, arg):
    try:
        msg = osc_message_builder.OscMessageBuilder(address=addr)
        msg.add_arg(arg)
        wing_sock.sendto(msg.build().dgram, (WING_IP, WING_TARGET_PORT))
    except: pass

def xilica_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PI_LISTEN_PORT)); s.listen(5)
    while running:
        conn, _ = s.accept()
        threading.Thread(target=handle_control_client, args=(conn,), daemon=True).start()

def wing_worker():
    last_poll = 0
    while running:
        if time.time() - last_poll > 2.0:
            wing_sock.sendto(b"/xremote\0\0\0\0", (WING_IP, WING_TARGET_PORT))
            last_poll = time.time()
        
        readable, _, _ = select.select([wing_sock], [], [], 0.5)
        for s in readable:
            data, addr = s.recvfrom(4096)
            try:
                path = data[:data.find(b'\0')].decode('latin-1')
                is_mute = "mute" in path
                target_key = None
                if "/main" in path: target_key = "mmute" if is_mute else "mv"
                else: 
                    m = re.search(r'/ch/(\d+)/', path)
                    if m: target_key = f"{m.group(1)}chm" if is_mute else f"{m.group(1)}chv"
                
                if not target_key: continue
                norm_key = normalize_key(target_key)
                
                val_f = None; val_i = None
                if len(data) >= 4:
                    if is_mute:
                        try: val_i = struct.unpack('>i', data[-4:])[0]
                        except: val_f = struct.unpack('>f', data[-4:])[0]
                    else:
                        for off in [0, 4, 8]:
                            st = len(data)-4-off
                            if st < 0: continue
                            try:
                                v = struct.unpack('>f', data[st:st+4])[0]
                                if -100.0 <= v <= 15.0 or 0.0 <= v <= 1.0: val_f = v; break
                            except: pass
                
                if val_i is not None: update_xilica_safely(norm_key, "TRUE" if val_i == 1 else "FALSE")
                elif val_f is not None:
                    if is_mute: update_xilica_safely(norm_key, "TRUE" if val_f == 1.0 else "FALSE")
                    else:
                        step = map_wing_to_step(val_f, norm_key)
                        update_xilica_safely(norm_key, step)
                        logger.info(f"📊 FB: {target_key} {val_f:.2f} -> {step}")
            except: pass

if __name__ == "__main__":
    for f in [connect_to_xilica, xilica_listener, wing_worker]: threading.Thread(target=f, daemon=True).start()
    while running: time.sleep(1)
