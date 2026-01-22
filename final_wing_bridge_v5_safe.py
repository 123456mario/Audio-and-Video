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
    0: -90.0, 
    1: -20.0, 
    2: -7.0,
    3: -5.0,
    4: -3.0, 
    5: 0.0,
    6: 3.0,   
    7: 5.0,
    8: 7.0,
    9: 10.0,
    10: 10.0
}

def map_step_to_db(step_val):
    try:
        idx = int(float(step_val))
        return VOL_MAP.get(idx, -90.0)
    except: return -90.0

# --- NETWORK ---
wing_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wing_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    wing_sock.bind(('0.0.0.0', WING_LOCAL_BIND_PORT))
    logger.info(f"✅ Wing Socket Bound to {WING_LOCAL_BIND_PORT}")
except Exception as e:
    logger.error(f"❌ Wing Bind Error: {e}")

xilica_sock = None

# --- XILICA SENDER (SAFE) ---
def connect_xilica_feedback():
    global xilica_sock
    while running:
        if xilica_sock is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((XILICA_IP, XILICA_FEEDBACK_PORT))
                logger.info(f"✅ Connected to Xilica Feedback")
                xilica_sock = s
            except: time.sleep(5)
        else: time.sleep(1)

def send_to_xilica_raw(cmd):
    global xilica_sock
    if xilica_sock:
        try:
            full_cmd = cmd.strip() + "\r"
            xilica_sock.sendall(full_cmd.encode())
        except: xilica_sock = None

def update_xilica_safely(key, value):
    # --- TIME LOCK CHECK ---
    # If user adjusted this control recently (< 2.0s), ignore feedback from Wing
    # to prevent "fighting" or stuttering behaviors.
    last_user_time = last_cmd_time.get(key, 0)
    if time.time() - last_user_time < 2.0:
        # logger.info(f"⏳ Ignoring Feedback (Time Lock): {key}") 
        return

    with cache_lock:
        last_val = xilica_value_cache.get(key)
        if last_val == value:
            return 
        xilica_value_cache[key] = value
    
    cmd = f"SET {key} {value}"
    if "chm" in key or "mmute" in key:
        cmd = f"SETRAW {key} {value}"
        
    logger.info(f"🛡️ Safe Update Xilica: {cmd}")
    send_to_xilica_raw(cmd)

# --- WING SENDER ---
def send_wing_osc(addr, arg):
    try:
        msg = osc_message_builder.OscMessageBuilder(address=addr)
        msg.add_arg(arg)
        packet = msg.build()
        wing_sock.sendto(packet.dgram, (WING_IP, WING_TARGET_PORT))
    except: pass

# --- CONTROL HANDLER (Xilica -> Wing) ---
def handle_control_client(conn):
    with conn:
        buffer = ""
        while running:
            try:
                data = conn.recv(1024)
                if not data: break
                buffer += data.decode(errors='ignore')
                while '\r' in buffer:
                    line, buffer = buffer.split('\r', 1)
                    process_control_cmd(line.strip())
            except: break

# --- TIME CACHE FOR ECHO SUPPRESSION ---
# Key: Xilica Key (e.g. "1chv", "MAIN_VOL"), Value: Timestamp of last user command
last_cmd_time = {}

def process_control_cmd(line):
    if not line: return
    logger.info(f"📥 RAW RECV: {line}")
    parts = line.split()
    if len(parts) < 3: return
    
    key = parts[1] 
    val = parts[2]
    
    # Check if Main 
    ch = None
    if "MAIN" in key.upper() or "MMUTE" in key.upper() or "MV" in key.upper(): 
        ch = "main"
    else:
        match = re.search(r'(\d+)', key)
        ch = match.group(1) if match else None
    
    if not ch: return

    # --- ECHO SUPPRESSION (Refined for Wing Master) ---
    val_cleaned = val.replace(".0", "")
    
    # 1. Update Time Cache (User might be touching)
    with cache_lock:
        last_cmd_time[key] = time.time()
        
        # 2. NUMERIC Comparison Check
        # If the value Xilica is sending is practically the same as what we just told it,
        # it is an ECHO. Ignore it.
        cached_val_str = xilica_value_cache.get(key)
        
        is_echo = False
        if cached_val_str is not None:
            try:
                # Compare as FLOAT to handle "10" vs "10.00" discrepancies
                v_in = float(val)
                v_cached = float(cached_val_str)
                if abs(v_in - v_cached) < 0.5: # Tolerance
                    is_echo = True
            except:
                # Fallback to string compare
                if cached_val_str == val_cleaned: is_echo = True
        
        if is_echo:
            logger.info(f"🚫 Ignoring Echo (Numeric): {key}={val} (Cached={cached_val_str})")
            return

        # If it's a NEW command (User Touch), update cache
        xilica_value_cache[key] = val_cleaned

    osc_addr = None
    osc_arg = None
    
    # ... (Mute/Vol logic follows)
    
    # RE-INSERTING MUTE/VOL LOGIC HERE TO ENSURE CONTEXT MATCH
    if "M" in key.upper() or "MUTE" in key.upper(): 
        is_volume = False
        if "V" in key.upper() or "VOL" in key.upper(): is_volume = True
            
        if not is_volume: 
            is_on = (val == "1" or val.upper() == "TRUE")
            if ch == "main": osc_addr = "/main/1/mute" 
            else: osc_addr = f"/ch/{ch}/mute"
            osc_arg = 1 if is_on else 0
            logger.info(f"🔇 Mute Set {key}: {osc_arg}")

    if ("V" in key.upper() or "VOL" in key.upper()) and osc_addr is None: 
        try:
            db_val = map_step_to_db(val) 
            if ch == "main": osc_addr = "/main/1/fdr" 
            else: osc_addr = f"/ch/{ch}/fdr"
            osc_arg = f"{db_val:.1f}" 
            logger.info(f"🎚 Vol Set {key}: {db_val}dB")
        except: pass

    if osc_addr and osc_arg is not None:
        send_wing_osc(osc_addr, osc_arg)

def xilica_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('0.0.0.0', PI_LISTEN_PORT))
        s.listen(5)
        logger.info(f"✅ Xilica Listener on {PI_LISTEN_PORT}")
        while running:
             conn, _ = s.accept()
             threading.Thread(target=handle_control_client, args=(conn,), daemon=True).start()
    except Exception as e:
        logger.error(f"❌ Listener Bind Error: {e}")

# --- WING FEEDBACK LOOP ---
def wing_worker():
    last_poll = 0
    poll_interval = 2.0 # Faster polling for better responsiveness
    
    while running:
        try:
            current_time = time.time()
            if current_time - last_poll > poll_interval:
                wing_sock.sendto(b"/xremote\0\0\0\0", (WING_IP, WING_TARGET_PORT))
                last_poll = current_time

            readable, _, _ = select.select([wing_sock], [], [], 0.5)
            for s in readable:
                data, addr = s.recvfrom(4096)
                if addr[0] != WING_IP: continue
                
                try:
                    null_idx = data.find(b'\0')
                    path = data[:null_idx].decode('latin-1')
                except: continue
                
                # Identify Target Key
                target_key = None
                is_mute = False
                
                if "/main/1" in path or "/main/st" in path: # COVER BOTH PATHS
                    if "fdr" in path or "fader" in path: target_key = "MAIN_VOL" 
                    elif "mute" in path: 
                        target_key = "mmute"
                        is_mute = True
                else:
                    ch_match = re.search(r'/ch/(\d+)/', path)
                    if ch_match:
                        ch = ch_match.group(1)
                        if "fdr" in path: target_key = f"{ch}chv"
                        elif "mute" in path: 
                             target_key = f"{ch}chm"
                             is_mute = True
                
                if not target_key: continue

                # ROBUST DATA EXTRACTION (Backwards Check 3 Steps)
                try:
                    val_bytes = None
                    final_val_f = None
                    final_val_i = None

                    # 1. Try Absolute Last 4 Bytes
                    if len(data) >= 4:
                        # MUTE HANDLING
                        if is_mute:
                            # Try Int
                            try:
                                v_i = struct.unpack('>i', data[-4:])[0]
                                if v_i == 0 or v_i == 1: final_val_i = v_i
                            except: pass
                            # Try Float if Int failed
                            if final_val_i is None:
                                try:
                                    v_f = struct.unpack('>f', data[-4:])[0]
                                    if v_f == 0.0 or v_f == 1.0: final_val_f = v_f
                                except: pass
                        else:
                            # VOLUME HANDLING - Backscan 3 steps for Valid Float
                            # Check -4, -8, -12 offsets
                            for offset in [0, 4, 8]:
                                start = len(data) - 4 - offset
                                if start < 0: continue
                                chunk = data[start:start+4]
                                try:
                                    v_f = struct.unpack('>f', chunk)[0]
                                    if 0.0 <= v_f <= 1.0: # Valid Range
                                        final_val_f = v_f
                                        break # Found it!
                                except: pass
                    
                    if final_val_i is not None:
                        cmd = "1" if final_val_i == 1 else "0"
                        update_xilica_safely(target_key, cmd) # MUTE FEEDBACK ENABLED
                    elif final_val_f is not None:
                        if is_mute:
                            cmd = "1" if final_val_f == 1.0 else "0"
                            update_xilica_safely(target_key, cmd) # MUTE FEEDBACK ENABLED
                        else:
                            # Volume Map 0-10
                            step = 0
                            val_f = final_val_f
                            if val_f >= 0.95: step = 10
                            elif val_f >= 0.88: step = 9
                            elif val_f >= 0.80: step = 8
                            elif val_f >= 0.73: step = 7 # 0dB region
                            elif val_f >= 0.65: step = 6
                            elif val_f >= 0.55: step = 5
                            elif val_f >= 0.45: step = 4
                            elif val_f >= 0.35: step = 3
                            elif val_f >= 0.20: step = 2
                            elif val_f >= 0.05: step = 1
                            else: step = 0
                            
                            # update_xilica_safely(target_key, f"{step}") # FEEDBACK DISABLED BY USER REQUEST
                except: pass

        except: pass

if __name__ == "__main__":
    t1 = threading.Thread(target=connect_xilica_feedback, daemon=True)
    t2 = threading.Thread(target=xilica_listener, daemon=True)
    t3 = threading.Thread(target=wing_worker, daemon=True)
    
    t1.start(); t2.start(); t3.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        running = False
