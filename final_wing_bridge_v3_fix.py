import socket
import threading
import time
import select
import logging
import struct
import re
from pythonosc import osc_message_builder

# --- CONFIGURATION ---
# 1. Xilica -> Pi (Control Input)
PI_LISTEN_PORT = 10025 

# 2. Pi -> Xilica (Feedback Output)
XILICA_IP = "192.168.1.20"
XILICA_FEEDBACK_PORT = 10007

# 3. Behringer Wing
WING_IP = "192.168.1.11"
WING_TARGET_PORT = 2223 
# CRITICAL: We MUST allow the OS to use the same port for Sending AND Listening
# to ensure the 'xremote' subscription is valid.
# But Wing often replies to the Source Port.
WING_LOCAL_BIND_PORT = 33901 

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("BridgeV3")

# --- GLOBAL SHARED RESOURCES ---
running = True

# Single UDP Socket for ALL Wing Communication (Symmetric)
# This ensures that when we send '/xremote', we do it from Port 33901,
# so Wing replies back to Port 33901.
wing_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wing_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    wing_sock.bind(('0.0.0.0', WING_LOCAL_BIND_PORT))
    logger.info(f"✅ Wing Socket Bound to {WING_LOCAL_BIND_PORT} (Symmetric Mode)")
except Exception as e:
    logger.error(f"❌ Failed to bind Wing socket: {e}")
    sys.exit(1)

# Xilica Sending Buffer (Queue could be better, but simple lock for now)
xilica_lock = threading.Lock()
xilica_sock = None

# --- MAPPING HELPERS ---
def map_1_to_10_to_db(val_1_10):
    try:
        val = max(1.0, min(10.0, float(val_1_10)))
        return -90.0 + ((val - 1.0) * (100.0 / 9.0))
    except: return -90.0

def map_db_to_1_to_10(db_val):
    try:
        val = max(-90.0, min(10.0, float(db_val)))
        return 1.0 + ((val + 90.0) * (9.0 / 100.0))
    except: return 1.0

# --- THREAD 1: XILICA FEEDBACK SENDER (To Port 10007) ---
def connect_xilica_feedback():
    global xilica_sock
    while running:
        if xilica_sock is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((XILICA_IP, XILICA_FEEDBACK_PORT))
                logger.info(f"✅ Connected to Xilica Feedback (Port {XILICA_FEEDBACK_PORT})")
                xilica_sock = s
            except:
                time.sleep(5) # Retry loop
        else:
            time.sleep(1)

def send_to_xilica(cmd):
    # Sends command to 10007
    global xilica_sock
    if xilica_sock:
        try:
            full_cmd = cmd.strip() + "\r"
            xilica_sock.sendall(full_cmd.encode())
            logger.info(f"📤 Feedback -> Xilica: {cmd}")
        except Exception as e:
            logger.error(f"Xilica Send Fail: {e}")
            xilica_sock = None

# --- THREAD 2: XILICA CONTROL LISTENER (From Port 10025) ---
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
    # Control Xilica -> Wing
    if not line: return
    logger.info(f"📥 Control <- Xilica: {line}")
    
    parts = line.split()
    if len(parts) < 3: return
    
    key = parts[1]
    val = parts[2]
    
    match = re.search(r'(\d+)', key)
    ch = match.group(1) if match else None
    if not ch: return

    osc_addr = None
    osc_arg = None

    # MUTE (Latch)
    if "M" in key.upper():
        is_on = (val == "1" or val.upper() == "TRUE")
        osc_addr = f"/ch/{ch}/mute"
        osc_arg = 1 if is_on else 0

    # VOLUME (Numeric)
    elif "V" in key.upper():
        try:
            db_val = map_1_to_10_to_db(val)
            osc_addr = f"/ch/{ch}/fdr"
            osc_arg = f"{db_val:.1f}" # Wing requires string for dB
        except: pass

    if osc_addr and osc_arg is not None:
        send_wing_osc(osc_addr, osc_arg)

def xilica_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PI_LISTEN_PORT))
    s.listen(5)
    logger.info(f"👂 Control Server Enabled on Port {PI_LISTEN_PORT}")
    while running:
        try:
            conn, _ = s.accept()
            threading.Thread(target=handle_control_client, args=(conn,), daemon=True).start()
        except: time.sleep(1)

# --- HELPER: SEND OSC ---
def send_wing_osc(addr, arg):
    # Build OSC Packet manually or via builder
    # Using builder for safety
    try:
        msg = osc_message_builder.OscMessageBuilder(address=addr)
        msg.add_arg(arg)
        packet = msg.build()
        wing_sock.sendto(packet.dgram, (WING_IP, WING_TARGET_PORT))
        # logger.info(f"🚀 To Wing: {addr} {arg}")
    except Exception as e:
        logger.error(f"OSC Build/Send Error: {e}")

# --- THREAD 3: WING FEEDBACK & SUBSCRIPTION ---
def wing_worker():
    # 1. Setup Polling / Subscription
    last_poll = 0
    
    # Select loop handles both Sending (Timer) and Receiving (IO)
    while running:
        try:
            current_time = time.time()
            
            # --- A. Periodic Subscription (Keep-Alive) ---
            if current_time - last_poll > 9.0:
                # Renew Subscription every 9 seconds
                # Must be sent from the same socket we listen on
                try:
                    # Generic Xremote
                    wing_sock.sendto(b"/xremote\0\0\0\0", (WING_IP, WING_TARGET_PORT))
                    last_poll = current_time
                except Exception as e:
                    logger.error(f"Sub Error: {e}")

            # --- B. Receive Feedback ---
            # Non-blocking check
            readable, _, _ = select.select([wing_sock], [], [], 0.5)
            for s in readable:
                data, addr = s.recvfrom(4096)
                if addr[0] != WING_IP: continue
                
                # Manual Parse
                null_idx = data.find(b'\0')
                if null_idx == -1: continue
                path = data[:null_idx].decode('latin-1')
                
                if "/fdr" in path or "/mute" in path:
                     # Parse Channel: /ch/1/fdr
                     ch_match = re.search(r'/ch/(\d+)/', path)
                     if not ch_match: continue
                     ch = ch_match.group(1)
                     
                     # Extract Value (Last 4 bytes usually float or int)
                     if len(data) >= 4:
                         if "fdr" in path: # FLOAT (0.0 - 1.0 Normalized)
                             val_f = struct.unpack('>f', data[-4:])[0]
                             # Convert to 1-10
                             # Wing Feedback is 0.0-1.0
                             db = -90.0 + (val_f * 100.0)
                             v_1_10 = map_db_to_1_to_10(db)
                             send_to_xilica(f"SET {ch}chv {v_1_10:.1f}")

                         elif "mute" in path: # INT (1 or 0)
                             val_i = struct.unpack('>i', data[-4:])[0]
                             # Sometimes Wing sends float for mute too, handle robustly
                             is_muted = False
                             if val_i < 10: is_muted = (val_i == 1)
                             else: # Try float
                                 val_f = struct.unpack('>f', data[-4:])[0]
                                 is_muted = (val_f > 0.5)
                             
                             cmd_val = "1" if is_muted else "0"
                             send_to_xilica(f"SETRAW {ch}chm {cmd_val}")
                             
        except Exception as e:
            # logger.error(f"Wing Loop Error: {e}")
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
