
import socket
import threading
import time
import logging
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
from pythonosc import osc_message_builder

# --- CONFIG ---
XILICA_PORT = 10025
WING_IP = "192.168.1.11"
WING_UDP_PORT = 2223

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("BridgeRestore")

running = True
osc_client = udp_client.SimpleUDPClient(WING_IP, WING_UDP_PORT)

# --- CLIENT MANAGEMENT ---
clients = set()
clients_lock = threading.Lock()

def send_broadcast(cmd):
    msg = cmd.strip() + "\r"
    encoded = msg.encode()
    with clients_lock:
        to_remove = set()
        for c in clients:
            try:
                c.sendall(encoded)
            except:
                to_remove.add(c)
        for c in to_remove:
            clients.remove(c)
    logger.info(f"📤 Broadcast: {cmd.strip()}")

# --- MAPPING ---
def map_fader_to_db(val):
    # Wing (0-1) -> dB (-90 to +10)
    try:
        v = float(val)
        return -90.0 + (v * 100.0)
    except: return -90.0

# --- HANDLERS ---
def handle_xilica_cmd(line):
    try:
        parts = line.upper().split()
        if len(parts) < 3: return
        key = parts[1]
        val_str = parts[2]
        
        # MAIN
        if key == "MV" or key == "MVOL":
            # Send String dB ("-10.0")
            osc_client.send_message("/main/1/fdr", val_str)
            osc_client.send_message("/main/st/fdr", val_str)
            logger.info(f"Vol -> {val_str}")
            return
        if key == "MMUTE" or key == "MAINMUTE":
            val = 1 if (val_str == "TRUE" or val_str == "1") else 0
            osc_client.send_message("/main/1/mute", val)
            osc_client.send_message("/main/st/mute", val)
            logger.info(f"Mute -> {val}")
            return
            
        # CHANNELS
        import re
        m = re.search(r'(\d+)', key)
        if m:
            ch = int(m.group(1))
            if "V" in key:
                 # Send String dB
                 osc_client.send_message(f"/ch/{ch}/fdr", val_str)
            elif "M" in key:
                 val = 1 if (val_str == "TRUE" or val_str == "1") else 0
                 osc_client.send_message(f"/ch/{ch}/mute", val)
                 
    except Exception as e:
        logger.error(f"Err: {e}")

def xilica_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', XILICA_PORT))
    s.listen(5)
    logger.info("TCP Server Started")
    
    while running:
        c, a = s.accept()
        with clients_lock: clients.add(c)
        threading.Thread(target=client_handler, args=(c,), daemon=True).start()

def client_handler(conn):
    with conn:
        while running:
            try:
                data = conn.recv(1024)
                if not data: break
                txt = data.decode(errors='ignore')
                for line in txt.replace('\r', '\n').split('\n'):
                    if line.strip(): handle_xilica_cmd(line)
            except: break
    with clients_lock: 
        if conn in clients: clients.remove(conn)

def osc_listener():
    # Polling & Listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 0)) # Ephemeral
    sock.settimeout(1.0)
    
    # Store socket for keepalive
    global osc_sock
    osc_sock = sock
    
    while running:
        # Keepalive
        try:
            sock.sendto(b"/xremote\0\0\0\0", (WING_IP, WING_UDP_PORT))
            
            # Recv loop
            start = time.time()
            while time.time() - start < 2.0:
                try:
                    data, addr = sock.recvfrom(4096)
                    # Basic Parse
                    null_idx = data.find(b'\0')
                    path = data[:null_idx].decode('latin-1')
                    
                    # Extract Val
                    import struct
                    fmt = '>f'
                    if "mute" in path: fmt = '>i'
                    val = struct.unpack(fmt, data[-4:])[0]
                    
                    # Feedback Logic
                    if "main" in path:
                        if "mute" in path:
                            is_on = (val==1)
                            send_broadcast(f"SET MMUTE {'TRUE' if is_on else 'FALSE'}")
                        elif "fdr" in path:
                            db = map_fader_to_db(val)
                            send_broadcast(f"SET MV {db:.1f}")
                    elif "/ch/" in path:
                        ch = path.split('/')[2]
                        if "mute" in path:
                            is_on = (val==1)
                            send_broadcast(f"SET {ch}CHM {'TRUE' if is_on else 'FALSE'}")
                        elif "fdr" in path:
                             db = map_fader_to_db(val)
                             send_broadcast(f"SET {ch}CHV {db:.1f}")
                             
                except socket.timeout: pass
                except Exception: pass
        except: time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=xilica_server, daemon=True).start()
    osc_listener()
