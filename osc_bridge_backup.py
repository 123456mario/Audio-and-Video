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

# Wing -> Python (OSC/UDP Listening)
# This is the port the Wing sends feedback TO. 
# CRITICAL: We must send /xremote FROM this port too.
OSC_LISTEN_IP = "0.0.0.0"
OSC_LISTEN_PORT = 10023 

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

# --- UDP SEND HELPER (Uses Listening Socket) ---
def send_osc_udp(address, value):
    try:
        msg = osc_message_builder.OscMessageBuilder(address=address)
        if value is not None:
             msg.add_arg(value)
        packet = msg.build()
        
        if osc_server_instance:
            # Send from the bound socket (Port 10023)
            osc_server_instance.socket.sendto(packet.dgram, (WING_IP, WING_UDP_PORT))
            # logger.info(f"📡 To Wing (Port 10023): {address} = {value}")
        else:
            logger.error("❌ OSC Server not ready yet")
            
    except Exception as e:
        logger.error(f"❌ UDP Send Error: {e}")

# --- KEEP ALIVE SUBSCRIPTION ---
def keep_alive_loop():
    logger.info("🔄 Starting Keep-Alive Loop (/xremote)")
    # Wait for server to init
    time.sleep(2) 
    
    while True:
        try:
            if osc_server_instance:
                # Send /xremote FROM 10023 using the server socket
                # Behringer mixers need an integer argument (usually 1)
                send_osc_udp("/xremote", 1)
                # logger.info("🔄 Sent Subscription Renewal from Port 10023") 
        except Exception as e:
            logger.error(f"❌ Keep-Alive Error: {e}")
        time.sleep(7)

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

def send_to_xilica(message):
    message = message.strip() + "\r"
    with clients_lock:
        if not connected_clients:
             logger.warning(f"⚠️ No Xilica clients connected. Cannot send: {message.strip()}")
        
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
            xilica_value = "true" if value >= 0.5 else "false"
        else:
            db_val = float(value)
            xilica_value = get_xilica_vol_from_db(db_val)
            
        if xilica_value is not None:
            cmd = f"SET {xilica_key} {xilica_value}"
            send_to_xilica(cmd)
            
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
                             # send_osc_udp(osc_addr, float(osc_val)) 
                        else:
                             try: 
                                 raw_val = float(val_str)
                                 int_val = int(raw_val)
                                 if int_val in VOL_MAP: osc_val = VOL_MAP[int_val]
                                 else: osc_val = -90.0
                                 logger.info(f"🎚️ Vol: {raw_val} -> {osc_val:.2f} dB")
                             except: pass
                        
                        if osc_val is not None and "mute" not in osc_addr.lower():
                            send_osc_udp(osc_addr, osc_val)
                            # logger.info(f"📡 To Wing: {osc_addr} = {osc_val}")
                
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
