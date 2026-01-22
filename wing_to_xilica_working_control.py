import socket
import threading
import time
import logging
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
from pythonosc import osc_message_builder

# --- CONFIGURATION ---
# --- CONFIGURATION ---
# Xilica Connection (TCP SERVER)
# Xilica will connect TO US on this port
XILICA_BIND_IP = "0.0.0.0"
XILICA_SERVER_PORT = 1500

# Behringer Wing Connection (OSC Listener)
# Listen on this port for updates FROM Wing
OSC_LISTEN_IP = "0.0.0.0"
OSC_LISTEN_PORT = 0 # Dynamic Port to avoid Bind Error (Safe Reset)

# Wing IP (for Keep-Alive / Handshake if needed)
WING_IP = "192.168.1.11"
WING_UDP_PORT = 2223
WING_HANDSHAKE_PORT = 2222

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("WingBridge")

# --- GLOBAL STATE ---
xilica_socket = None
xilica_lock = threading.Lock()
running = True
osc_server_socket = None 

# OSC Client for reliable sending (Separate from Listener)
osc_client = udp_client.SimpleUDPClient(WING_IP, WING_UDP_PORT)

# --- HELPER: VALUE MAPPING ---
def map_fader_to_db(value):
    """
    Map Wing OSC Float (0.0 - 1.0) to Xilica dB (-90.0 to +10.0)
    """
    try:
        val_float = float(value)
        # Heuristic: If 0.0-1.0, treat as normalized
        if 0.0 <= val_float <= 1.0:
            # Linear Map: 0.0 -> -90, 1.0 -> +10
            # Range = 100dB
            db_val = -90.0 + (val_float * 100.0) 
            return db_val
        else:
            # Already dB?
            return val_float
    except:
        return -90.0


def map_db_to_fader(db_val):
    """
    Map Xilica dB (-90.0 to +10.0) to Wing OSC Float (0.0 - 1.0)
    Inverse of map_fader_to_db
    """
    try:
        val = float(db_val)
        # Clamp dB first to expected range
        if val < -90.0: val = -90.0
        if val > 10.0: val = 10.0
        
        # Linear Map Inverse: 0.0 = -90, 1.0 = +10 ==> Range 100
        norm_val = (val + 90.0) / 100.0
        return max(0.0, min(1.0, norm_val))
    except:
        return 0.0

# --- HELPERS: SEND TO WING ---
# We use the same socket logic as the Scanner/KeepAlive
# --- HELPERS: SEND TO WING ---
# We use the same socket logic as the Scanner/KeepAlive
def send_to_wing_osc(address, args):
    try:
        # Use SimpleUDPClient (Standard python-osc)
        # REVERTED TO GOLDEN STATE (Mute worked with this)
        if osc_client:
            osc_client.send_message(address, args)
            logger.info(f"📤 Sent to Wing: {address} {args}")
        else:
             logger.error("❌ OSC Client is None!")
            
    except Exception as e:
        logger.error(f"Error sending OSC: {e}")

def send_to_wing_fader(ch_num, db_val):
    try:
        # 1-based Indexing (Confirmed)
        ch_int = int(ch_num)
        
        # PROTOCOL FIX: Wing wants STRING format for dB values (e.g., "-10.0")
        # Do not normalize to 0.0-1.0 float.
        val_str = str(float(db_val))
        
        path = f"/ch/{ch_int}/fdr"
        
        logger.info(f"🎯 Firing Vol: {path} -> '{val_str}' (String)")
        send_to_wing_osc(path, val_str)
        
        # Also send to Main Mix fader if needed? Usually /ch/X/fdr is enough.
        # If user wants mix send level, that's different.
            
    except ValueError:
        logger.error(f"Invalid Channel Number: {ch_num}")

def send_to_wing_mute(ch_num, is_muted):
    try:
        # 1-based Indexing
        ch_int = int(ch_num)
        
        # Integer 1/0 (Confirmed)
        val_int = 1 if is_muted else 0 
        
        path = f"/ch/{ch_int}/mute"
        # Optional: /ch/{ch_int}/mix/on (inverted) logic could be added if requested
        
        logger.info(f"🎯 Firing Mute: {path} -> {val_int} (Int)")
        send_to_wing_osc(path, val_int)
        
    except ValueError:
        logger.error(f"Invalid Channel Number: {ch_num}")
# --- XILICA SERVER (Multi-Threaded) ---
clients = set()
clients_lock = threading.Lock()

def start_xilica_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((XILICA_BIND_IP, XILICA_SERVER_PORT))
        server.listen(5) # Allow multiple connections
        logger.info(f"🎧 Listening for Xilica TCP on {XILICA_BIND_IP}:{XILICA_SERVER_PORT}")
    except Exception as e:
        logger.error(f"❌ Failed to bind Xilica Server: {e}")
        return

    while running:
        try:
            conn, addr = server.accept()
            # Spawn a thread for EACH client
            t = threading.Thread(target=handle_xilica_client, args=(conn, addr))
            t.daemon = True
            t.start()
        except Exception as e:
            if running:
                logger.error(f"Accept Error: {e}")
                time.sleep(1)

def handle_xilica_client(conn, addr):
    logger.info(f"🔗 Xilica Connected from {addr}")
    
    with clients_lock:
        clients.add(conn)
        
    try:
        while running:
            data = conn.recv(1024)
            if not data: break
            
            text = data.decode(errors='ignore')
            logger.info(f"💾 RAW XILICA: {repr(text)}")
            
            lines = text.replace('\r', '\n').split('\n')
            for line in lines:
                line = line.strip()
                if line: handle_xilica_command(line)
    except Exception as e:
        logger.error(f"Client Error {addr}: {e}")
    finally:
        logger.warning(f"Xilica Disconnected {addr}")
        with clients_lock:
            if conn in clients: clients.remove(conn)
        conn.close()

import re

def handle_xilica_command(cmd_raw):
    """
    Parse Xilica Command: 
    SET CH1M 1, SET CH1V -10.0, SET MMUTE 1, SET MV -10.0
    """
    try:
        cmd = cmd_raw.strip().upper()
        parts = cmd.split()
        if len(parts) < 3: return
        if parts[0] != "SET": return
        
        key = parts[1]
        val_str = parts[2]

        # Case 1: Main Mix (mapped to Main 1 / Main Matrix 1)
        if key == "MV" or key == "MVOL":
            val = float(val_str)
            
            # SMART MAPPING: 0-10 Scale -> -90~+10 dB
            if val >= 0:
                final_db = (val * 10.0) - 90.0
            else:
                final_db = val
                
            val_str_db = f"{final_db:.1f}"
            logger.info(f"📥 Main Vol: {val} (Scale 0-10) -> {val_str_db} dB")
            send_to_wing_osc("/main/1/fdr", val_str_db)
            return

        if key == "MMUTE":
            is_muted = (val_str == "TRUE" or val_str == "1" or val_str == "ON")
            logger.info(f"📥 Main Mute (Target Main 1): {is_muted}")
            val_int = 1 if is_muted else 0
            
            # Primary Target: Main 1
            send_to_wing_osc("/main/1/mute", val_int)
            
            # Optional: Also send to ST
            # send_to_wing_osc("/main/st/mute", val_int)
            return

        # Case 2: Channels
        match = re.search(r'(\d+)', key)
        if match:
            ch_num = match.group(1)
            
            if key.endswith("V") or "VOL" in key or "FDR" in key:
                 val = float(val_str)
                 # SMART MAPPING: 0-10 Scale -> -90~+10 dB
                 if val >= 0:
                     db_val = (val * 10.0) - 90.0
                 else:
                     db_val = val
                     
                 logger.info(f"📥 Xilica Vol: Ch {ch_num} ({key}) -> {val} (Scale 0-10) -> {db_val:.1f} dB")
                 send_to_wing_fader(ch_num, db_val)
                 
            elif key.endswith("M") or "MUTE" in key:
                 is_muted = (val_str == "TRUE" or val_str == "1" or val_str == "ON")
                 logger.info(f"📥 Xilica Mute: Ch {ch_num} ({key}) -> {is_muted}")
                 send_to_wing_mute(ch_num, is_muted)
                 
    except Exception as e:
        logger.error(f"Cmd Parse Error '{cmd_raw}': {e}")

def send_to_xilica(command_str):
    # Broadcast to ALL connected clients (Mute Module AND Volume Module)
    command_str = command_str.strip() + "\r"
    encoded = command_str.encode()
    
    with clients_lock:
        if not clients: return
        
        # Iterate over a copy to avoid modification issues
        for conn in list(clients):
            try:
                conn.sendall(encoded)
            except Exception as e:
                logger.error(f"❌ Send Error: {e}")
    
    logger.info(f"📤 Sent to Xilica (Broadcast): {command_str.strip()}")

# --- OSC HANDLERS ---

def handle_mute(address, *args):
    """
    Handle Mute Messages
    Address: /ch/1/mute -> SET 1CHM TRUE/FALSE
    """
    try:
        if not args: return
        val = args[0]
        logger.info(f"Rx MUTE: {address} {val}")
        
        parts = address.split('/')
        if len(parts) >= 3 and parts[1] == 'ch':
            ch_num = parts[2]
            
            # Wing Mute: 1 = Muted, 0 = Unmuted
            is_muted = (val == 1 or val == 1.0 or val == '1')
            
            # Xilica: Use 'TRUE' / 'FALSE'
            xilica_val = "TRUE" if is_muted else "FALSE"
            
            # Key: 1chm (LOWERCASE to match Xilica 3rd Party config)
            # Cmd: set 1chm TRUE
            cmd = f"set {ch_num}chm {xilica_val}"
            send_to_xilica(cmd)
            
    except Exception as e:
        logger.error(f"Error handling mute {address}: {e}")

def handle_fader(address, *args):
    """
    Handle Fader Messages
    Address: /ch/1/fdr -> set 1chv [0-100]
    """
    try:
        if not args: return
        val = args[0]
        
        parts = address.split('/')
        if len(parts) >= 3 and parts[1] == 'ch':
            ch_num = parts[2]
            
            # Wing sends normalized float (0.0-1.0) usually via OSC? 
            # Wait, our previous logs showed Wing sends NO arguments in query? 
            # Or sends float? Assuming float 0.0-1.0 from map_fader_to_db logic.
            # map_fader_to_db converts 0.0-1.0 to -90~+10 dB.
            
            db_val = map_fader_to_db(val)
            
            # REVERSE SMART MAPPING: -90~+10 dB -> 0-10 Xilica
            # Formula: xilica = (db + 90) / 10
            xilica_val = (db_val + 90.0) / 10.0
            
            if xilica_val < 0: xilica_val = 0.0
            if xilica_val > 10: xilica_val = 10.0
            
            # Key: 1chv (LOWERCASE)
            cmd = f"set {ch_num}chv {xilica_val:.1f}"
            send_to_xilica(cmd)
            
    except Exception as e:
        logger.error(f"Error handling fader {address}: {e}")

def handle_main_mute(address, *args):
    """ Main Mute: set mmute TRUE/FALSE """
    try:
        if not args: return
        val = args[0]
        # Wing Main is Int 1/0
        is_muted = (val == 1 or val == 1.0)
        xilica_val = "TRUE" if is_muted else "FALSE"
        
        # LOWERCASE mmute
        send_to_xilica(f"set mmute {xilica_val}")
    except: pass

def handle_main_fader(address, *args):
    """ Main Fader: set mvol [0-100] """
    try:
        if not args: return
        val = args[0]
        
        db_val = map_fader_to_db(val)
        
        # REVERSE SMART MAPPING (0-10 Scale)
        xilica_val = (db_val + 90.0) / 10.0
        
        if xilica_val < 0: xilica_val = 0.0
        if xilica_val > 10: xilica_val = 10.0
        
        # LOWERCASE mvol
        send_to_xilica(f"set mvol {xilica_val:.1f}")
    except: pass




def handle_any(address, *args):
    """ Catch-all for debugging """
    logger.info(f"Rx UNKNOWN: {address} {args}")

# --- KEEP ALIVE for WING ---
# IMPORTANT: Must send from the SAME PORT (10023) we are listening on
def wing_keep_alive():
    logger.info("🔄 Starting Wing Keep-Alive Loop (Source Port Preserved)...")
    
    # OSC Message: /xremote (Classic Behringer Subscription)
    # The bytes for "/xremote\0\0\0\0,\0\0\0"
    probe_info = osc_message_builder.OscMessageBuilder(address="/?").build().dgram
    probe_root = osc_message_builder.OscMessageBuilder(address="/").build().dgram
    xremote_msg = osc_message_builder.OscMessageBuilder(address="/xremote").build().dgram
    # node_msg = osc_message_builder.OscMessageBuilder(address="/node").build().dgram # Optional
    fader_query = osc_message_builder.OscMessageBuilder(address="/ch/1/fdr").build().dgram

    while running:
        try:
            if osc_server_socket:
                # Send to Wing using the LISTENING socket
                logger.info("💓 Sending Keep-Alive (Batch + Query)...")
                osc_server_socket.sendto(xremote_msg, (WING_IP, WING_UDP_PORT))
                osc_server_socket.sendto(probe_info, (WING_IP, WING_UDP_PORT))
                # osc_server_socket.sendto(probe_root, (WING_IP, WING_UDP_PORT))
                osc_server_socket.sendto(fader_query, (WING_IP, WING_UDP_PORT))
            else:
                logger.warning("⚠️ OSC Socket not ready yet")
                
        except Exception as e:
            logger.error(f"Keep-Alive Error: {e}")
            
        time.sleep(5) 

# --- MAIN RAW SOCKET VERSION ---
def main():
    global osc_server_socket, running
    logger.info("🚀 Starting Wing -> Xilica Bridge (Raw Socket Mode)")
    
    # Threads for Xilica
    t_xilica = threading.Thread(target=start_xilica_server)
    t_xilica.daemon = True
    t_xilica.start()
    
    # Setup Dispatcher
    disp = dispatcher.Dispatcher()
    for i in range(1, 11): 
        disp.map(f"/ch/{i}/mute", handle_mute)
        disp.map(f"/ch/{i}/mix/on", handle_mute)
        disp.map(f"/ch/{i}/fdr", handle_fader)
        disp.map(f"/ch/{i}/mix/fader", handle_fader)
    disp.map("/main/st/mute", handle_main_mute)
    disp.map("/main/st/mix/on", handle_main_mute)
    disp.map("/main/st/fdr", handle_main_fader)
    disp.map("/main/st/mix/fader", handle_main_fader)
    disp.set_default_handler(handle_any)

    # Raw Socket Setup (Like Scanner)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((OSC_LISTEN_IP, OSC_LISTEN_PORT))
    
    # Store for Keep-Alive
    osc_server_socket = udp_sock
    
    local_port = udp_sock.getsockname()[1]
    logger.info(f"👂 Listening for OSC on {OSC_LISTEN_IP}:{local_port}")
    
    # Start Keep-Alive Thread
    t_alive = threading.Thread(target=wing_keep_alive)
    t_alive.daemon = True
    t_alive.start()

    # Receive Loop
    try:
        while running:
            try:
                data, addr = udp_sock.recvfrom(4096)
                if not data: continue
                
                # Try simple decode to check validity
                # Python-OSC dispatcher expects bytes
                try:
                    disp.call_handlers_for_packet(data, addr)
                except Exception as e:
                    logger.error(f"OSC Parse Error from {addr}: {e}")
                    # logger.info(f"Raw received {len(data)} bytes: {data.hex()}")
                    
            except socket.timeout:
                continue
            except Exception as e:
                if running:
                    logger.error(f"UDP Recv Error: {e}")
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        logger.info("🛑 Stopping...")
        running = False
        udp_sock.close()

if __name__ == "__main__":
    main()
