import socket
import threading
import time
import logging
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder

# logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# --- CONFIGURATION ---
# Xilica -> Python (TCP)
TCP_SERVER_IP = "0.0.0.0" 
TCP_SERVER_PORT = 1500     # Keep User Preference

# Python -> Wing (OSC/UDP)
WING_IP = "192.168.1.11"
WING_UDP_PORT = 2223 
WING_HANDSHAKE_PORT = 2222 # For "WING?" handshake

# Wing -> Python (OSC/UDP Listening)
# This is the port the Wing sends feedback TO. 
OSC_LISTEN_IP = "0.0.0.0"
OSC_LISTEN_PORT = 10023 # Changed to 10023 to avoid port collision

XILICA_IP = "192.168.1.20"
XILICA_PORT = 10007 

# --- VOL MAPPING (1-10 Strategy) ---
VOL_MAP = {
    1: -60.0,
    2: -40.0,
    3: -30.0,
    4: -20.0, # Requested
    5: -10.0,
    6: 0.0,   # Unity
    7: 2.5,   # Requested
    8: 5.0,   # Requested
    9: 7.5,   # Requested
    10: 10.0  # Max
}

# Reverse Map for Feedback (Approximate)
def get_xilica_vol_from_db(db_val):
    if db_val <= -61.0: return "0" 
    closest_key = 1
    min_diff = 1000.0
    for k, v in VOL_MAP.items():
        diff = abs(db_val - v)
        if diff < min_diff:
            min_diff = diff
            closest_key = k
    return str(closest_key)

# Global Server Reference (to access socket for sending)
osc_server_instance = None

# --- UDP SEND HELPER ---
def send_udp_raw(port, message_bytes):
    try:
         if osc_server_instance:
             osc_server_instance.socket.sendto(message_bytes, (WING_IP, port))
    except Exception as e:
        logger.error(f"❌ Raw UDP Send Error: {e}")

def send_osc_udp(address, value):
    try:
        msg = osc_message_builder.OscMessageBuilder(address=address)
        if value is not None:
             msg.add_arg(value)
        packet = msg.build()
        
        if osc_server_instance:
            # Send from the bound socket (Port 10023)
            osc_server_instance.socket.sendto(packet.dgram, (WING_IP, WING_UDP_PORT))
        else:
            logger.error("❌ OSC Server not ready yet")
            
    except Exception as e:
        logger.error(f"❌ UDP Send Error: {e}")

# --- KEEP ALIVE SUBSCRIPTION ---
def keep_alive_loop():
    logger.info("🔄 Starting Handshake & Keep-Alive Loop (Wing Protocol - Port 10023)")
    # Wait for server to init
    time.sleep(2) 
    
    while True:
        try:
            if osc_server_instance:
                # 1. HANDSHAKE: Send "WING?" to Port 2222
                send_udp_raw(WING_HANDSHAKE_PORT, b"WING?") 
                time.sleep(0.05)
                
                # 2. SUBCRIPTION BARRAGE (Targeting Port 10023)
                
                # Variant A: Explicit Port 10023
                send_osc_udp("/%#10023/*s~", None)
                send_osc_udp("/%#10023/*S~", None)
                
                # Variant B: Generic Global
                send_osc_udp("/*s~", None)
                
                # Variant C: Legacy
                send_osc_udp("/xremote", 1)
                
                # /node
                send_osc_udp("/node", None)
 
        except Exception as e:
            logger.error(f"❌ Keep-Alive Error: {e}")
        
        time.sleep(4) 

# --- POLLING LOOP (Fallback for Missing Feedback) ---
def polling_loop():
    logger.info("🔄 Starting Active Polling Loop (Sync Fallback)")
    time.sleep(3) # Wait for init
    
    # Create list of addresses to query
    query_targets = []
    for i in range(1, 11):
        query_targets.append(f"/ch/{i}/fdr")
        query_targets.append(f"/ch/{i}/mute")
    query_targets.append(OSC_ADDR_MAIN_FADER)
    query_targets.append(OSC_ADDR_MAIN_MUTE)
    
    idx = 0
    while True:
        try:
            if osc_server_instance:
                # Query a batch of parameters so we don't flood too fast, 
                # but cover everything within a few seconds.
                # Send 4 queries per 0.5s tick = 8 queries per sec. 
                # Total 22 queries -> Full cycle every ~2.75 sec.
                for _ in range(4): # 4 queries per burst
                    if idx < len(query_targets):
                        addr = query_targets[idx]
                        # sending without args = Query in OSC
                        send_osc_udp(addr, None)
                        idx = (idx + 1) % len(query_targets)
                    else:
                        idx = 0
        except Exception as e:
            logger.error(f"Polling Error: {e}")
            
        time.sleep(0.5) 

# --- MAPPING ---
OSC_ADDR_MAIN_FADER = "/main/1/fdr" 
OSC_ADDR_MAIN_MUTE = "/main/1/mute"

CONTROL_MAP = {}
for i in range(1, 10):
    CONTROL_MAP[f"ch{i}v"] = f"/ch/{i}/fdr"
    CONTROL_MAP[f"ch{i}vol"] = f"/ch/{i}/fdr"
    CONTROL_MAP[f"ch{i}m"] = f"/ch/{i}/mute"

CONTROL_MAP["mv"] = OSC_ADDR_MAIN_FADER
CONTROL_MAP["MAIN_VOL"] = OSC_ADDR_MAIN_FADER
CONTROL_MAP["MAIN_MUTE"] = OSC_ADDR_MAIN_MUTE
CONTROL_MAP["mmute"] = OSC_ADDR_MAIN_MUTE

OSC_TO_XILICA_MAP = {}
for k, v in CONTROL_MAP.items():
    if k.endswith("v") or k.endswith("m") or k == "mv" or k == "mmute":
        OSC_TO_XILICA_MAP[v] = k

# --- XILICA SENDER (TCP Feedback) ---
connected_clients = []
clients_lock = threading.Lock()
last_sent_values = {} # Cache to prevent echo loop
last_sent_lock = threading.Lock()

def update_last_sent(key, val):
    with last_sent_lock:
        last_sent_values[key] = str(val)

def check_is_echo(key, val):
    with last_sent_lock:
        last = last_sent_values.get(key)
        return last == str(val)

def send_to_xilica(message):
    message = message.strip() + "\r"
    with clients_lock:
        if not connected_clients:
             pass
        
        to_remove = []
        for conn in connected_clients:
            try:
                conn.sendall(message.encode('utf-8'))
                logger.info(f"📤 Feedback to Xilica: {message.strip()}")
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                to_remove.append(conn)
        
        for conn in to_remove:
            connected_clients.remove(conn)

# --- OSC SERVER (LISTENER) ---
def osc_handler(address, *args):
    try:
        # ENABLE DEBUG LOGGING TO SEE RECEPTION
        logger.info(f"👂 From Wing: {address} {args}")
        
        if not args: return
        value = args[0]
        
        xilica_key = OSC_TO_XILICA_MAP.get(address)
        if not xilica_key: return 
            
        xilica_value = None
        if "mute" in address:
            try:
                # Ensure value is float for comparison
                val_float = float(value)
                xilica_value = "true" if val_float >= 0.5 else "false"
            except ValueError:
                xilica_value = "false"
                logger.error(f"❌ Failed to convert mute value: {value}")
        else:
            if value == '-oo':
                db_val = -90.0 # Treat -infinity as bottom
            else:
                try:
                   db_val = float(value)
                except ValueError:
                   db_val = -90.0
                   logger.error(f"❌ Failed to convert fader value: {value}")
                   
            xilica_value = get_xilica_vol_from_db(db_val)
            
        if xilica_value is not None:
            # CHECK FOR ECHO BEFORE SENDING
            if not check_is_echo(xilica_key, xilica_value):
                # Only send if it's a NEW change from the Wing physically
                cmd = f"SET {xilica_key} {xilica_value}"
                send_to_xilica(cmd)
            else:
                logger.debug(f"🔇 Suppressed Echo: {xilica_key}={xilica_value}")
            
    except Exception as e:
        logger.error(f"OSC Handler Error: {e}")

def start_osc_server():
    global osc_server_instance
    disp = dispatcher.Dispatcher()
    for osc_addr in OSC_TO_XILICA_MAP.keys():
        disp.map(osc_addr, osc_handler)
    
    # Catch-all for unknown messages (debugging)
    disp.set_default_handler(osc_handler)

    osc_server_instance = osc_server.ThreadingOSCUDPServer((OSC_LISTEN_IP, OSC_LISTEN_PORT), disp)
    logger.info(f"✅ OSC Feedback Server Listening on {OSC_LISTEN_IP}:{OSC_LISTEN_PORT}")
    osc_server_instance.serve_forever()

# --- XILICA CONNECTION HANDLER ---
def handle_client(conn, addr):
    logger.info(f"✅ Xilica Connected: {addr}")
    with clients_lock:
        connected_clients.append(conn)
        
    try:
        while True:
            data = conn.recv(1024)
            if not data: break
            
            lines = data.decode('utf-8', errors='ignore').split('\r')
            for line in lines:
                line = line.strip()
                if not line: continue
                logger.info(f"📥 From Xilica: {line}")
                parts = line.split()
                
                if len(parts) >= 3 and parts[0].upper() == "SET":
                    key = parts[1]
                    val_str = parts[2]
                    
                    osc_addr = None
                    for k in CONTROL_MAP:
                        if k.lower() == key.lower():
                            osc_addr = CONTROL_MAP[k]
                            break
                    
                    if osc_addr:
                        osc_val = None
                        if "mute" in osc_addr.lower():
                             if val_str == "1" or val_str.upper() == "TRUE": osc_val = 1 
                             else: osc_val = 0
                             # Send Int & Float for Mute
                             send_osc_udp(osc_addr, int(osc_val))
                             
                        else:
                             try: 
                                 raw_val = float(val_str)
                                 int_val = int(raw_val)
                                 if int_val in VOL_MAP: osc_val = VOL_MAP[int_val]
                                 else: osc_val = -90.0
                                 logger.info(f"🎚️ Vol: {raw_val} -> {osc_val:.2f} dB")
                             except: pass
                        
                        if osc_val is not None:
                            if "mute" not in osc_addr.lower():
                                send_osc_udp(osc_addr, osc_val)
                                
                            # LOCAL ECHO LOGIC
                            # send_to_xilica(f"SET {key} {val_str}") <-- REMOVED local echo to fix loop
                            # Instead, update cache so we ignore the inevitable UDP feedback
                            update_last_sent(key, val_str)
                
    except Exception as e:
        logger.error(f"Handler Error: {e}")
    finally:
        with clients_lock:
            if conn in connected_clients:
                connected_clients.remove(conn)
        conn.close()
        logger.info(f"❌ Xilica Disconnected: {addr}")

# --- MAIN SERVER ---
def run_server():
    keep_alive = threading.Thread(target=keep_alive_loop)
    keep_alive.daemon = True
    keep_alive.start()

    poll_thread = threading.Thread(target=polling_loop)
    poll_thread.daemon = True
    poll_thread.start()

    osc_thread = threading.Thread(target=start_osc_server)
    osc_thread.daemon = True
    osc_thread.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((TCP_SERVER_IP, TCP_SERVER_PORT))
        server.listen(5)
        logger.info(f"✅ Standalone Bridge Running on TCP Port {TCP_SERVER_PORT}")
        
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
            
    except Exception as e:
        logger.error(f"Server Error: {e}")

if __name__ == "__main__":
    run_server()
