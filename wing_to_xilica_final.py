import socket
import threading
import time
import select
import logging
import struct
from pythonosc import udp_client
from pythonosc import osc_message_builder

# --- CONFIGURATION ---
# Xilica Connection (TCP SERVER)
XILICA_BIND_IP = "0.0.0.0"
XILICA_SERVER_PORT = 1500

# Behringer Wing Connection
WING_IP = "192.168.1.11"
WING_UDP_PORT = 2223
WING_LISTEN_PORT = 33901 # Fixed Listening Port

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("WingBridge")

# --- GLOBAL STATE ---
clients = set()
clients_lock = threading.Lock()
running = True
osc_sock = None 

# OSC Client for sending ONLY (using separate port for control is safer)
osc_client = udp_client.SimpleUDPClient(WING_IP, WING_UDP_PORT)

# --- MAPPING HELPERS (1-10 Scale) ---
def map_1_to_10_to_db(val_1_10):
    """
    Map User Scale (1-10) to Wing dB (-90.0 to +10.0)
    1  = -90.0 dB (Min)
    10 = +10.0 dB (Max)
    5.5 = -40 dB (Approx mid)
    """
    try:
        val = float(val_1_10)
        # Clamp to 1-10
        val = max(1.0, min(10.0, val))
        
        # Linear Interpolation
        # Input Range: 9 (10-1)
        # Output Range: 100 (10 - -90)
        # Ratio: 100 / 9 = 11.11...
        
        db_val = -90.0 + ((val - 1.0) * (100.0 / 9.0))
        return db_val
    except:
        return -90.0

def map_db_to_1_to_10(db_val):
    """
    Map Wing dB (-90.0 to +10.0) to User Scale (1-10)
    """
    try:
        val = float(db_val)
        # Clamp dB
        val = max(-90.0, min(10.0, val))
        
        # Linear Inverse
        # (val - min_out) / range_out = (x - min_in) / range_in
        # x = min_in + (ratio * (val - min_out))
        # Ratio = 9 / 100 = 0.09
        
        user_val = 1.0 + ((val + 90.0) * (9.0 / 100.0))
        return max(1.0, min(10.0, user_val))
    except:
        return 1.0

def map_wing_float_to_db(val_float):
    """ Convert Wing OSC Float (0.0-1.0) to dB """
    # 0.0 -> -90, 1.0 -> +10
    return -90.0 + (val_float * 100.0)

# --- XILICA SERVER ---
def start_xilica_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((XILICA_BIND_IP, XILICA_SERVER_PORT))
        server.listen(5)
        logger.info(f"🎧 Listening for Xilica TCP on {XILICA_BIND_IP}:{XILICA_SERVER_PORT}")
    except Exception as e:
        logger.error(f"❌ Failed to bind Xilica Server: {e}")
        return

    while running:
        try:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_xilica_client, args=(conn, addr))
            t.daemon = True
            t.start()
        except Exception as e:
            if running: time.sleep(1)

def handle_xilica_client(conn, addr):
    logger.info(f"🔗 Xilica Connected from {addr}")
    with clients_lock: clients.add(conn)
    try:
        while running:
            data = conn.recv(1024)
            if not data: break
            text = data.decode(errors='ignore')
            lines = text.replace('\r', '\n').split('\n')
            for line in lines:
                if line.strip(): handle_xilica_cmd(line.strip())
    except: pass
    finally:
        logger.warning(f"Xilica Disconnected {addr}")
        with clients_lock: 
            if conn in clients: clients.remove(conn)
        conn.close()

def send_to_xilica(cmd):
    # Broadcast to Xilica (Feedback)
    cmd = cmd.strip() + "\r"
    encoded = cmd.encode()
    with clients_lock:
        if not clients: return
        for c in list(clients):
            try: c.sendall(encoded)
            except: pass
    logger.info(f"📤 To Xilica: {cmd.strip()}")

# --- LOGIC HANDLER ---
import re

def handle_xilica_cmd(cmd_raw):
    # Expected: SET [NAME] [VAL]
    # Names: Mute Latch (e.g. 1chm), Numeric (e.g. 1chv)
    try:
        cmd = cmd_raw.upper()
        parts = cmd.split()
        if len(parts) < 3: return
        
        # 1. SETRAW (Latch Button support)
        # Xilica sends: SETRAW 1chm 1
        if parts[0] == "SETRAW":
            key = parts[1]
            val = parts[2]
            
            # Extract Channel
            match = re.search(r'(\d+)', key)
            if match:
                ch = match.group(1)
                is_muted = (val == "1")
                # Send to Wing
                # Wing Mute: 1 = Mute, 0 = Unmute
                osc_val = 1 if is_muted else 0
                logger.info(f"🎚 Xilica Latch: {key} -> Wing Mute {osc_val}")
                osc_client.send_message(f"/ch/{ch}/mute", osc_val)
                return

        # 2. SET (Numeric support)
        # Xilica sends: SET 1chv 5.5
        if parts[0] == "SET":
            key = parts[1]
            val_str = parts[2]
            
            match = re.search(r'(\d+)', key)
            if match:
                ch = match.group(1)
                
                # Check if it is Volume (Numeric)
                if "V" in key or "VOL" in key:
                    val_1_10 = float(val_str)
                    db_val = map_1_to_10_to_db(val_1_10)
                    
                    # Wing requires String for dB
                    db_str = f"{db_val:.1f}"
                    logger.info(f"🎚 Xilica Numeric: {val_1_10} -> Wing dB {db_str}")
                    osc_client.send_message(f"/ch/{ch}/fdr", db_str)
                    
                # Check if it is Mute (Standard SET)
                elif "M" in key or "MUTE" in key:
                    # Some Xilica versions send SET for buttons
                    is_muted = (val_str == "TRUE" or val_str == "1")
                    osc_val = 1 if is_muted else 0
                    osc_client.send_message(f"/ch/{ch}/mute", osc_val)

    except Exception as e:
        logger.error(f"Cmd Error: {e}")

# --- OSC LISTENER & FEEDBACK ---
POLL_TARGETS = [f"/ch/{i}/fdr" for i in range(1, 9)] + [f"/ch/{i}/mute" for i in range(1, 9)]

def osc_loop():
    global osc_sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', WING_LISTEN_PORT))
    sock.setblocking(False)
    osc_sock = sock
    logger.info(f"👂 UDP Listener active on {WING_LISTEN_PORT}")
    
    # Poll Loop Thread
    threading.Thread(target=poller, args=(sock,), daemon=True).start()
    
    inputs = [sock]
    while running:
        try:
            readable, _, _ = select.select(inputs, [], [], 1.0)
            for s in readable:
                data, addr = s.recvfrom(4096) 
                if addr[0] != WING_IP: continue
                
                # Manual Simple Parsing for Speed/Robustness
                try:
                    # Find address end
                    null_idx = data.find(b'\0')
                    if null_idx == -1: continue
                    path = data[:null_idx].decode('latin-1')
                    
                    osc_val = None
                    # Parse Float (Fader) or Int (Mute)
                    # Standard Wing format: Address, Tytpetag (,f or ,i), Value
                    # We assume last 4 bytes are value for simple types
                    if len(data) >= 4:
                        if "fdr" in path: # Float
                            osc_val = struct.unpack('>f', data[-4:])[0]
                            # Wing sends 0.0-1.0 Normalized Float in feedback?
                            # Need to convert to dB, then to 1-10
                            db_val = map_wing_float_to_db(osc_val)
                            val_1_10 = map_db_to_1_to_10(db_val)
                            
                            ch = re.search(r'(\d+)', path).group(1)
                            # Feedback to Xilica Numeric: SET 1chv 5.5
                            send_to_xilica(f"SET {ch}chv {val_1_10:.1f}")
                            
                        elif "mute" in path: # Int
                            # Wing Mute Feedback often has multiple tags but value is simple
                            # Sometimes it's int 1/0, sometimes float 1.0/0.0
                            # Check byte structure or try both
                            try:
                                i_val = struct.unpack('>i', data[-4:])[0]
                                if i_val > 100: raise ValueError # Not an int
                                is_muted = (i_val == 1)
                            except:
                                f_val = struct.unpack('>f', data[-4:])[0]
                                is_muted = (f_val > 0.5)
                            
                            ch = re.search(r'(\d+)', path).group(1)
                            # Feedback to Xilica Latch: SETRAW 1chm 1
                            cmd = "1" if is_muted else "0"
                            send_to_xilica(f"SETRAW {ch}chm {cmd}")
                            
                except Exception as e:
                    # logger.error(f"Parse error: {e}")
                    pass
        except KeyboardInterrupt: break
        except: time.sleep(0.1)

def poller(sock):
    """ Active Polling to keep Wing sending feedback """
    dest = (WING_IP, WING_UDP_PORT)
    while running:
        try:
            # Renew Subscription
            sock.sendto(b"/xremote\0\0\0\0", dest)
            time.sleep(9) # xremote lasts 10s
        except: time.sleep(1)

if __name__ == "__main__":
    t_osc = threading.Thread(target=osc_loop, daemon=True)
    t_osc.start()
    
    start_xilica_server()
