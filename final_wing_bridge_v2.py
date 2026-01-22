import socket
import threading
import time
import select
import logging
import struct
import re
from pythonosc import udp_client

# --- USER CONFIGURATION (STRICTLY FOLLOWED) ---
# 1. Xilica -> Pi (Control Input)
# Pi listens on this port. Xilica sends commands here.
PI_LISTEN_PORT = 10025 

# 2. Pi -> Xilica (Feedback Output)
# Pi sends feedback values to this target.
XILICA_IP = "192.168.1.30"
XILICA_TARGET_PORT = 10007

# 3. Behringer Wing
WING_IP = "192.168.1.11"
WING_RX_PORT = 2223  # Wing listening port
WING_TX_PORT = 33901 # Pi listening port for Wing feedback

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Bridge")

# --- GLOBAL STATE ---
running = True
osc_sock = None
xilica_sock_out = None # Client socket for sending to 10007

# OSC Client (Pi -> Wing)
wing_client = udp_client.SimpleUDPClient(WING_IP, WING_RX_PORT)

# --- MAPPING: Numeric 1-10 <-> Wing dB ---
def map_1_to_10_to_db(val_1_10):
    try:
        val = float(val_1_10)
        val = max(1.0, min(10.0, val)) # Clamp 1~10
        # Map: 1 -> -90dB, 10 -> +10dB
        db_val = -90.0 + ((val - 1.0) * (100.0 / 9.0))
        return db_val
    except: return -90.0

def map_db_to_1_to_10(db_val):
    try:
        val = float(db_val)
        val = max(-90.0, min(10.0, val))
        # Map: -90dB -> 1, +10dB -> 10
        user_val = 1.0 + ((val + 90.0) * (9.0 / 100.0))
        return max(1.0, min(10.0, user_val))
    except: return 1.0

def db_to_wing_str(db_val):
    return f"{db_val:.1f}"

# --- THREAD 1: Xilica FEEDBACK SENDER (Client to 10007) ---
def xilica_sender_thread():
    global xilica_sock_out
    while running:
        if xilica_sock_out is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5.0)
                s.connect((XILICA_IP, XILICA_TARGET_PORT))
                logger.info(f"✅ Connected to Xilica Feedback Port {XILICA_TARGET_PORT}")
                xilica_sock_out = s
            except Exception as e:
                # logger.warning(f"Connecting to Xilica {XILICA_TARGET_PORT} failed: {e}")
                time.sleep(5)
        else:
            time.sleep(1) # Alive wait

def send_to_xilica_10007(cmd):
    global xilica_sock_out
    if not xilica_sock_out: return
    try:
        full_cmd = cmd.strip() + "\r"
        xilica_sock_out.sendall(full_cmd.encode())
        logger.info(f"📤 To Xilica (10007): {cmd}")
    except Exception as e:
        logger.error(f"Xilica Send Error: {e}")
        xilica_sock_out.close()
        xilica_sock_out = None

# --- THREAD 2: Xilica CONTROL LISTENER (Server on 10025) ---
def handle_xilica_incoming(conn):
    with conn:
        buffer = ""
        while running:
            try:
                data = conn.recv(1024)
                if not data: break
                buffer += data.decode(errors='ignore')
                while '\r' in buffer:
                    line, buffer = buffer.split('\r', 1)
                    process_xilica_cmd(line.strip())
            except: break

def process_xilica_cmd(line):
    if not line: return
    logger.info(f"📥 From Xilica (10025): {line}")
    parts = line.split()
    if len(parts) < 3: return
    
    cmd_type = parts[0].upper() # SET or SETRAW
    key = parts[1]
    val = parts[2]
    
    # Extract Channel
    match = re.search(r'(\d+)', key)
    ch = match.group(1) if match else None
    if not ch: return

    # 1. Latch Button (Mute) -> SETRAW
    if "SETRAW" in cmd_type or "M" in key.upper(): 
        # Logic: 1 = Mute On, 0 = Mute Off
        if val == "1" or val.upper() == "TRUE": 
            wing_val = 1
        else: 
            wing_val = 0
            
        logger.info(f"🎚 Control: Ch{ch} Mute -> {wing_val}")
        wing_client.send_message(f"/ch/{ch}/mute", wing_val)

    # 2. Numeric (Volume 1~10) -> SET
    elif "V" in key.upper():
        try:
            vol_1_10 = float(val)
            db_val = map_1_to_10_to_db(vol_1_10)
            db_str = db_to_wing_str(db_val)
            
            logger.info(f"🎚 Control: Ch{ch} Vol {vol_1_10} -> {db_str} dB")
            wing_client.send_message(f"/ch/{ch}/fdr", db_str)
        except: pass

def xilica_listener_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PI_LISTEN_PORT))
    s.listen(5)
    logger.info(f"👂 Listening for Xilica Control on Port {PI_LISTEN_PORT}")
    
    while running:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_xilica_incoming, args=(conn,), daemon=True).start()
        except: time.sleep(1)

# --- THREAD 3: Wing FEEDBACK LISTENER (UDP 33901) ---
def wing_feedback_thread():
    global osc_sock
    osc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    osc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    osc_sock.bind(('0.0.0.0', WING_TX_PORT))
    osc_sock.setblocking(False)
    logger.info(f"👂 Listening for Wing on Port {WING_TX_PORT}")
    
    inputs = [osc_sock]
    while running:
        try:
            readable, _, _ = select.select(inputs, [], [], 1.0)
            for s in readable:
                data, addr = s.recvfrom(4096)
                if addr[0] != WING_IP: continue
                
                # Simple OSC Parse (Address + Value)
                try:
                    null_idx = data.find(b'\0')
                    path = data[:null_idx].decode('latin-1')
                    
                    if "fdr" in path or "mute" in path:
                         # Extract Ch
                         match = re.search(r'ch/(\d+)', path)
                         if not match: continue
                         ch = match.group(1)
                         
                         if len(data) >= 4:
                            # 1. VOLUME (/fdr)
                            if "fdr" in path:
                                # Parse Float (Wing sends normalized 0.0-1.0 OR dB float?)
                                # Usually feedback from Wing is Float 0.0-1.0
                                val_f = struct.unpack('>f', data[-4:])[0]
                                
                                # Convert Normalized(0-1) -> dB -> 1~10
                                db = -90.0 + (val_f * 100.0)
                                val_1_10 = map_db_to_1_to_10(db)
                                
                                # Send to Xilica (Numeric)
                                send_to_xilica_10007(f"SET {ch}chv {val_1_10:.1f}")
                                
                            # 2. MUTE (/mute)
                            elif "mute" in path:
                                # Try as Int
                                try:
                                    val_i = struct.unpack('>i', data[-4:])[0]
                                    is_muted = (val_i == 1)
                                except:
                                    # Try as Float
                                    val_f = struct.unpack('>f', data[-4:])[0]
                                    is_muted = (val_f > 0.5)
                                
                                # Send to Xilica (Latch Button -> SETRAW)
                                cmd_val = "1" if is_muted else "0"
                                send_to_xilica_10007(f"SETRAW {ch}chm {cmd_val}")

                except Exception as e: pass
        except: pass

# --- THREAD 4: POLL LOOP ---
def poll_loop():
    # Keep subscriptions alive
    dest = (WING_IP, WING_RX_PORT)
    while running:
        if osc_sock:
            try:
                osc_sock.sendto(b"/xremote\0\0\0\0", dest)
            except: pass
        time.sleep(8)

# --- MAIN ---
if __name__ == "__main__":
    t1 = threading.Thread(target=xilica_sender_thread, daemon=True)
    t2 = threading.Thread(target=xilica_listener_thread, daemon=True)
    t3 = threading.Thread(target=wing_feedback_thread, daemon=True)
    t4 = threading.Thread(target=poll_loop, daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        running = False
