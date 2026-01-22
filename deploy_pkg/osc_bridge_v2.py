import asyncio
import logging
import socket
import sys
import threading
from typing import Optional

# Ensure the local behringer_mixer library is findable
sys.path.append("/home/pi/behringer-mixer") 

from behringer_mixer import mixer_api

# --- CONFIGURATION ---
WING_IP = "192.168.1.11"
WING_PORT = 2223 # Default UDP port for Wing
XILICA_IP = "192.168.1.20"
XILICA_PORT = 10001 # Xilica listening port
BRIDGE_PORT = 10001 # Pi listening port for Xilica

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("osc_bridge_v2")

# Global Mixer Instance
mixer = None

# --- MAPPINGS ---
# Xilica Key -> Wing Library Address
# Using the internal names from mixer_type_wing.py
# e.g. /ch/1/fdr -> /ch/1/mix_fader (dB)
XILICA_TO_WING = {}
WING_TO_XILICA = {}

def build_mappings():
    # Channel Faders & Mutes
    for i in range(1, 41): # 40 Channels on Wing usually
        # Faders (dB)
        x_key_vol = f"ch{i}v" if i > 1 else "ch1v" # Handle ch1v vs ch1vol based on observation
        if i == 1: 
            XILICA_TO_WING["ch1vol"] = f"/ch/{i}/mix_fader"
            XILICA_TO_WING["ch1v"] = f"/ch/{i}/mix_fader"
        else:
            XILICA_TO_WING[f"ch{i}v"] = f"/ch/{i}/mix_fader"
            
        WING_TO_XILICA[f"/ch/{i}/mix_fader"] = f"ch{i}v"
        
        # Mutes
        x_key_mute = f"ch{i}m"
        XILICA_TO_WING[x_key_mute] = f"/ch/{i}/mix_on"
        WING_TO_XILICA[f"/ch/{i}/mix_on"] = x_key_mute

    # Main Fader & Mute
    XILICA_TO_WING["MAIN_VOL"] = "/main/1/mix_fader"
    XILICA_TO_WING["mainvol"] = "/main/1/mix_fader"
    XILICA_TO_WING["mv"] = "/main/1/mix_fader"
    WING_TO_XILICA["/main/1/mix_fader"] = "MAIN_VOL"

    XILICA_TO_WING["MAIN_MUTE"] = "/main/1/mix_on"
    XILICA_TO_WING["mmute"] = "/main/1/mix_on"
    WING_TO_XILICA["/main/1/mix_on"] = "MAIN_MUTE"


build_mappings()

# --- XILICA COMMS ---
connected_clients = []
client_lock = threading.Lock()

def broadcast_to_xilica(key, value):
    """Sends feedback to Xilica. Value is already converted by the library."""
    # Convert value: Library uses True/False for mutes, dB for faders?
    # mixer_type_wing says 'boolean_inverted' for mutes.
    # We need to standardize for Xilica: "TRUE"/"FALSE" for mutes, Float for faders.
    
    final_val = value
    if isinstance(value, bool):
        final_val = "TRUE" if value else "FALSE"
        # Since 'mix_on' = True means Sound ON (Unmuted), 
        # But Xilica 'mute' usually means Mute ON. 
        # CAUTION: Check Xilica logic. Usually "Mute=TRUE" means Silent.
        # Wing Library 'mix_on': True=AudioOn, False=Muted.
        # Therefore: If mix_on is True, Mute is FALSE.
        # Let's verify mixer_type_wing logic.
        pass
        
    cmd = f"SET {key} {final_val}\r"
    encoded_cmd = cmd.encode()
    
    logger.info(f"📤 To Xilica: {cmd.strip()}")

    # Hybrid Send: Broadcast + Push
    sent_any = False
    
    with client_lock:
        to_remove = []
        for conn in connected_clients:
            try:
                conn.sendall(encoded_cmd)
                sent_any = True
            except:
                to_remove.append(conn)
        for dead in to_remove:
            connected_clients.remove(dead)
            
    if not sent_any:
        # Fallback Push
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((XILICA_IP, 10007)) # Try default control port? or 10001?
            # User said 10007 initially, but Broadcast uses 10001 connections.
            # Let's stick to 10001 if possible, but Xilica is Server there?
            # Actually Xilica listens on 10007 usually for external control?
            sock.send(encoded_cmd)
            sock.close()
        except Exception as e:
            logger.warning(f"Failed to push to Xilica: {e}")

# --- WING CALLBACK ---
def start_wing_listener(data):
    """Callback from Behringer Mixer Library"""
    # data is a dict: {'property': '/ch/1/mix_fader', 'value': -10.5}
    key_path = data.get('property')
    value = data.get('value')
    
    if key_path in WING_TO_XILICA:
        xilica_key = WING_TO_XILICA[key_path]
        
        # Inversion Logic Check
        # If library returns 'mix_on' (True=On), and Xilica 'mute' (True=Muted)
        if key_path.endswith("mix_on"):
             # mix_on=True -> Mute=False
             # mix_on=False -> Mute=True
             # But let's check what Xilica expects for "ch1m".
             # Usually "ch1m=TRUE" is Muted.
             final_val = not value # Invert bool
             broadcast_to_xilica(xilica_key, final_val)
        else:
            broadcast_to_xilica(xilica_key, value)

# --- TCP SERVER (Xilica Listener) ---
async def xilica_server_handler(reader, writer):
    addr = writer.get_extra_info('peername')
    logger.info(f"Connected Xilica Client: {addr}")
    
    # Add to broadcast list (we need the raw socket for that, asyncio writer is different)
    # Use a wrapper or just keep writer?
    # For simplicity in this hybrid script, we might need a bridge.
    # Actually, asyncio writers can be stored.
    
    # BUT, the `broadcast` function above uses `socket.send`. 
    # Mixing asyncio and threads/sockets is tricky.
    # Let's keep it simple: ALL ASYNC.
    
    # Store writer for broadcasting
    with client_lock:
        # We'll store the writer object directly in a separate list for Async?
        # Or adapt existing list.
        # Let's append to a global set of writers.
        pass

    try:
        while True:
            data = await reader.read(1024)
            if not data: break
            message = data.decode().strip()
            logger.info(f"📥 From Xilica: {message}")
            
            # Message Parsing: "SET ch1vol -10.0"
            parts = message.split()
            if len(parts) >= 3 and parts[0] == "SET":
                key = parts[1]
                val_str = parts[2]
                
                # Logic
                if key in XILICA_TO_WING:
                    wing_addr = XILICA_TO_WING[key]
                    
                    # Convert Value
                    target_val = val_str
                    if "TRUE" in val_str: target_val = False # Mute=True -> MixOn=False
                    elif "FALSE" in val_str: target_val = True
                    else:
                        try: target_val = float(val_str)
                        except: pass
                    
                    # Send to Wing
                    await mixer.set_value(wing_addr, target_val)

    except Exception as e:
        logger.error(f"Xilica Handler Error: {e}")
    finally:
        logger.info(f"Disconnected Xilica Client: {addr}")

async def run_xilica_server():
    server = await asyncio.start_server(xilica_server_handler, '0.0.0.0', BRIDGE_PORT)
    logger.info(f"Xilica Server listening on {BRIDGE_PORT}")
    async with server:
        await server.serve_forever()

# --- MAIN ---
async def main():
    global mixer
    logger.info("Starting OSC Bridge V2...")
    
    # 1. Init Mixer
    mixer = mixer_api.create("WING", ip=WING_IP, port=WING_PORT, delay=0.002)
    
    # 2. Start Mixer Connection
    await mixer.start()
    logger.info("Wing Mixer Connected!")
    
    # 3. Subscribe
    await mixer.subscribe(start_wing_listener)
    logger.info("Subscribed to Wing Updates")
    
    # 4. Start Xilica Server
    await run_xilica_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
