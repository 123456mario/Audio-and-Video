
import socket
import threading
import time
import struct
import logging
import re

# --- CONFIG ---
WING_IP = "192.168.1.11"
WING_PORT = 2223

XILICA_LISTEN_PORT = 10025
BRIDGE_PORT = 33901 

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Bridge")

# --- GLOBAL STATE ---
sock_osc = None
active_xilica_conn = None 
last_known_values = {}

POLL_TARGETS = [
    "/ch/1/fdr", "/ch/1/mute",
    "/ch/2/fdr", "/ch/2/mute",
    "/ch/3/fdr", "/ch/3/mute",
    "/ch/4/fdr", "/ch/4/mute",
    "/ch/5/fdr", "/ch/5/mute",
    "/ch/6/fdr", "/ch/6/mute",
    "/ch/7/fdr", "/ch/7/mute",
    "/ch/8/fdr", "/ch/8/mute",
    "/ch/9/fdr", "/ch/9/mute",
    "/main/1/fdr", "/main/1/mute"
]

def map_db_to_xilica(db_val):
    val = (db_val + 90.0) / 10.0
    if val < 0: val = 0.0
    if val > 10: val = 10.0
    return val

def map_xilica_to_db(val_0_10):
    db = (val_0_10 * 10.0) - 90.0
    return db

# --- XILICA COMMUNICATION ---
def send_to_xilica(cmd):
    if not cmd.endswith('\r\n'): 
        cmd = cmd.rstrip() + '\r\n'
    try:
        global active_xilica_conn
        if active_xilica_conn:
            try:
                active_xilica_conn.send(cmd.encode())
            except:
                logger.warning("Active Xilica connection lost.")
                active_xilica_conn = None
    except Exception as e:
        logger.error(f"Xilica Send Err: {e}")

def start_xilica_server():
    s = None
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', XILICA_LISTEN_PORT)) 
            s.listen(5)
            logger.info(f"✅ Xilica Control Server Started on {XILICA_LISTEN_PORT}")
            break
        except Exception as e:
            logger.error(f"❌ Xilica Port {XILICA_LISTEN_PORT} Busy. Retrying in 2s... ({e})")
            if s:
                try: s.close()
                except: pass
            time.sleep(2)
    
    while True:
        try:
            conn, addr = s.accept()
            logger.info(f"🟢 Xilica Client Connected from {addr}")
            global active_xilica_conn
            active_xilica_conn = conn
            threading.Thread(target=handle_xilica_client, args=(conn,), daemon=True).start()
        except Exception as e:
            logger.error(f"Xilica Accept Err: {e}")
            time.sleep(1)

def handle_xilica_client(conn):
    with conn:
        buffer = ""
        while True:
            try:
                data = conn.recv(1024)
                if not data: 
                    logger.info("Xilica Client Disconnected")
                    global active_xilica_conn
                    if active_xilica_conn == conn: active_xilica_conn = None
                    break
                
                raw_txt = data.decode(errors='ignore')
                buffer += raw_txt
                
                while '\r' in buffer:
                    line, buffer = buffer.split('\r', 1)
                    process_xilica_cmd(line.strip())
            except Exception as e:
                logger.error(f"Xilica Handler Err: {e}")
                break

def get_channel_number(key_str):
    match = re.search(r'\d+', key_str)
    if match:
        return match.group()
    return None

# --- OSC HELPER ---
def build_osc_packet(addr_str, type_tag, val):
    # Address Padding
    addr = addr_str.encode()
    pad = 4 - (len(addr) % 4)
    addr += b'\0' * pad
    
    # Type Tag Padding
    tag = type_tag.encode()
    pad = 4 - (len(tag) % 4)
    tag += b'\0' * pad
    
    data = b''
    if type_tag == ',i':
        data = struct.pack('>i', int(val))
    elif type_tag == ',f':
        data = struct.pack('>f', float(val))
        
    return addr + tag + data

def process_xilica_cmd(line):
    if not line: return
    logger.info(f"📥 Processing Xilica Cmd: '{line}'")
    
    try:
        parts = line.split()
        if len(parts) < 3: return
        key = parts[1].upper() # 1CHV
        val_str = parts[2]
        
        osc_addr = None
        osc_val = None
        osc_type = None
        
        # Channel Volume
        if "CH" in key and "V" in key:
            try:
                val = float(val_str)
                ch = get_channel_number(key)
                if ch:
                    osc_addr = f"/ch/{ch}/fdr"
                    osc_val = map_xilica_to_db(val)
                    osc_type = ',f'
            except: pass
            
        # Channel Mute
        elif "CH" in key and "M" in key:
            try:
                ch = get_channel_number(key)
                if ch:
                    osc_addr = f"/ch/{ch}/mute"
                    v_up = val_str.upper()
                    is_on = (v_up == "TRUE" or v_up == "1" or v_up == "ON")
                    osc_val = 1 if is_on else 0
                    osc_type = ',i'
            except: pass
            
        # Main Volume
        elif "MVOL" in key or "MV" in key:
            try:
                val = float(val_str)
                osc_addr = "/main/1/fdr"
                osc_val = map_xilica_to_db(val)
                osc_type = ',f'
            except: pass

        # Main Mute
        elif "MMUTE" in key or "MAINMUTE" in key:
            try:
                v_up = val_str.upper()
                is_on = (v_up == "TRUE" or v_up == "1" or v_up == "ON")
                osc_addr = "/main/1/mute"
                osc_val = 1 if is_on else 0
                osc_type = ',i'
            except: pass

        if osc_addr and sock_osc and osc_type:
            pkt = build_osc_packet(osc_addr, osc_type, osc_val)
            sock_osc.sendto(pkt, (WING_IP, WING_PORT))
            logger.info(f"📤 Sent to Wing: {osc_addr} {osc_val}")
            
    except Exception as e:
        logger.error(f"Cmd handle err: {e}")

# --- OSC RECEIVER & POLLER ---
def main():
    global sock_osc
    logger.info("🚀 STARTING BRIDGE v4.4 (SETRAW for Mute)")
    
    sock_osc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_osc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock_osc.bind(('0.0.0.0', BRIDGE_PORT))
    except Exception as e:
        logger.error(f"Bind Fail: {e}")
        return

    t = threading.Thread(target=start_xilica_server, daemon=True)
    t.start()
    
    def receiver():
        while True:
            try:
                data, addr = sock_osc.recvfrom(4096)
                if addr[0] != WING_IP: continue
                
                # Check for mute packet
                
                end_idx = data.find(b'\0')
                if end_idx == -1: continue
                osc_addr = data[:end_idx].decode('latin-1')
                
                if osc_addr in POLL_TARGETS:
                    val_offset = len(data) - 4
                    val = None
                    
                    if "mute" in osc_addr:
                         val = struct.unpack('>i', data[val_offset:])[0]
                    else:
                         val = struct.unpack('>f', data[val_offset:])[0]
                            
                    last = last_known_values.get(osc_addr)
                    is_change = False
                    if last is None: is_change = True
                    elif abs(val - last) > 0.001: is_change = True
                    
                    if is_change:
                        last_known_values[osc_addr] = val
                        xilica_cmd = ""
                        
                        if "/fdr" in osc_addr:
                            x_val = map_db_to_xilica(val)
                            # Volume uses standard SET with float string
                            if "/ch/" in osc_addr:
                                ch = osc_addr.split('/')[2]
                                xilica_cmd = f"SET {ch}chv {x_val:.1f}"
                            elif "/main/" in osc_addr:
                                xilica_cmd = f"SET mvol {x_val:.1f}"
                        
                        elif "/mute" in osc_addr:
                            # Mute uses SETRAW with Integer 1/0
                            is_on = (val >= 1)
                            x_val = 1 if is_on else 0
                            
                            if "/ch/" in osc_addr:
                                ch = osc_addr.split('/')[2]
                                xilica_cmd = f"SETRAW {ch}chm {x_val}"
                            elif "/main/" in osc_addr:
                                xilica_cmd = f"SETRAW mmute {x_val}"
                                
                        if xilica_cmd:
                            logger.info(f"⬅️ Feedback: {osc_addr} {val} -> {xilica_cmd}")
                            send_to_xilica(xilica_cmd)

            except Exception as e:
                pass
                
    t_recv = threading.Thread(target=receiver, daemon=True)
    t_recv.start()
    
    logger.info("🔄 Starting Polling...")
    idx = 0
    while True:
        try:
            for path in POLL_TARGETS:
                # Correct Polling Query
                q = path.encode()
                pad = 4 - (len(q) % 4)
                q += b'\0' * pad
                sock_osc.sendto(q, (WING_IP, WING_PORT))
                time.sleep(0.002) 
            
            if idx % 20 == 0:
                 sock_osc.sendto(b"/xremote\0\0\0\0", (WING_IP, WING_PORT))

            idx += 1
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Poll Err: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
