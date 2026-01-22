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
logger = logging.getLogger("BridgeV5_Fix")

running = True

# --- VOLUME MAP (0-9) ---
VOL_MAP = {
    0: -90.0,
    1: -60.0,
    2: -40.0,
    3: -30.0,
    4: -5.0,
    5: -3.0,
    6: 0.0,
    7: 3.0,
    8: 5.0,
    9: 10.0
}

def map_step_to_db(step_val):
    try:
        idx = int(float(step_val))
        val = VOL_MAP.get(idx, -90.0)
        logger.info(f"🔍 Map: Input={step_val} -> {val} dB")
        return val
    except: return -90.0

def map_db_to_step(db_val):
    closest_step = 0
    min_diff = 1000.0
    for step, target_db in VOL_MAP.items():
        diff = abs(db_val - target_db)
        if diff < min_diff:
            min_diff = diff
            closest_step = step
    return float(closest_step)

# --- NETWORK ---
wing_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wing_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    wing_sock.bind(('0.0.0.0', WING_LOCAL_BIND_PORT))
    logger.info(f"✅ Wing Socket Bound to {WING_LOCAL_BIND_PORT}")
except Exception as e:
    logger.error(f"❌ Wing Bind Error: {e}")
    sys.exit(1)

# SHARED UDP SOCKET for SENDING Control to Wing (Symmetric)
# We use 'wing_sock' for both sending and receiving to maintain port symmetry

xilica_lock = threading.Lock()
xilica_sock = None

# --- STATE CACHE (Prevent Feedback Loops) ---
# Stores the last value SENT to Xilica to avoid re-triggering logic
last_sent_to_xilica = {} 
cache_lock = threading.Lock()

def update_cache(key, val):
    with cache_lock:
        last_sent_to_xilica[key] = str(val)

def is_echo(key, val):
    with cache_lock:
        last = last_sent_to_xilica.get(key)
        return last == str(val)

# --- THREADS ---
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

def send_to_xilica_feedback(cmd):
    # Sends command to 10007 (Feedback Only)
    global xilica_sock
    if xilica_sock:
        try:
            full_cmd = cmd.strip() + "\r"
            xilica_sock.sendall(full_cmd.encode())
            logger.info(f"📤 Feedback -> Xilica: {cmd}")
        except: xilica_sock = None

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

def process_control_cmd(line):
    # Handle COMMAND from Xilica (Port 10025)
    if not line: return
    
    parts = line.split()
    if len(parts) < 3: return
    
    key = parts[1]
    val = parts[2]
    
    # FILTER: If this value is what WE just sent to Xilica, ignore it (Echo)
    # But wait, 10025 is Control Input. Usually Xilica sends here when USER touches screen.
    # Feedback goes to 10007.
    # So 10025 traffic is almost always User Action.
    
    logger.info(f"📥 Control <- Xilica: {line}") 

    match = re.search(r'(\d+)', key)
    ch = match.group(1) if match else None
    if not ch: return

    osc_addr = None
    osc_arg = None

    if "M" in key.upper(): # MUTE
        is_on = (val == "1" or val.upper() == "TRUE")
        osc_addr = f"/ch/{ch}/mute"
        osc_arg = 1 if is_on else 0

    elif "V" in key.upper(): # VOLUME
        try:
            db_val = map_step_to_db(val) 
            osc_addr = f"/ch/{ch}/fdr"
            osc_arg = f"{db_val:.1f}"
        except: pass

    if osc_addr and osc_arg is not None:
        send_wing_osc(osc_addr, osc_arg)

def xilica_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PI_LISTEN_PORT))
    s.listen(5)
    while running:
        try:
             conn, _ = s.accept()
             threading.Thread(target=handle_control_client, args=(conn,), daemon=True).start()
        except: time.sleep(1)

def send_wing_osc(addr, arg):
    try:
        # Use the SAME socket (wing_sock) for sending
        # This ensures Port 33901 is the source port
        msg = osc_message_builder.OscMessageBuilder(address=addr)
        msg.add_arg(arg)
        packet = msg.build()
        wing_sock.sendto(packet.dgram, (WING_IP, WING_TARGET_PORT))
        # logger.info(f"🚀 Wing Tx: {addr} {arg}") # Debug
    except Exception as e:
        logger.error(f"OSC Send Error: {e}")

def wing_worker():
    last_poll = 0
    while running:
        try:
            current_time = time.time()
            if current_time - last_poll > 9.0:
                try:
                    # Generic Xremote subscription from 33901
                    wing_sock.sendto(b"/xremote\0\0\0\0", (WING_IP, WING_TARGET_PORT))
                    last_poll = current_time
                except: pass

            readable, _, _ = select.select([wing_sock], [], [], 0.5)
            for s in readable:
                data, addr = s.recvfrom(4096)
                if addr[0] != WING_IP: continue
                
                null_idx = data.find(b'\0')
                if null_idx == -1: continue
                path = data[:null_idx].decode('latin-1')
                
                # Feedback Analysis
                if "/fdr" in path or "/mute" in path:
                     ch_match = re.search(r'/ch/(\d+)/', path)
                     if not ch_match: continue
                     ch = ch_match.group(1)
                     
                     if len(data) >= 4:
                         if "fdr" in path: 
                             val_f = struct.unpack('>f', data[-4:])[0]
                             db = -90.0 + (val_f * 100.0)
                             
                             # Map to Step
                             step_val_f = map_db_to_step(db)
                             step_val = f"{step_val_f:.0f}"
                             
                             key = f"{ch}chv"
                             
                             # Only send if changed (Echo Suppression)
                             if not is_echo(key, step_val):
                                 update_cache(key, step_val)
                                 send_to_xilica_feedback(f"SET {key} {step_val}")

                         elif "mute" in path:
                             val_i = struct.unpack('>i', data[-4:])[0]
                             is_muted = (val_i == 1)
                             cmd_val = "1" if is_muted else "0"
                             key = f"{ch}chm"

                             if not is_echo(key, cmd_val):
                                 update_cache(key, cmd_val)
                                 send_to_xilica_feedback(f"SETRAW {key} {cmd_val}")

        except Exception as e: 
            # logger.error(f"Loop error: {e}")
            pass

if __name__ == "__main__":
    t1 = threading.Thread(target=connect_xilica_feedback, daemon=True)
    t2 = threading.Thread(target=xilica_listener, daemon=True)
    t3 = threading.Thread(target=wing_worker, daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        running = False
