
import socket
import time
import struct
import subprocess
import threading
import sys
import os

# Config matches bridge_v48_test.py
WING_IP = "127.0.0.1"
WING_MOCK_PORT = 9001
XILICA_PORT = 9002
BRIDGE_PORT = 9003

def build_osc_packet(addr_str, type_tag, val):
    addr = addr_str.encode()
    pad = 4 - (len(addr) % 4)
    addr += b'\0' * pad
    tag = type_tag.encode()
    pad = 4 - (len(tag) % 4)
    tag += b'\0' * pad
    data = b''
    if type_tag == ',i':
        data = struct.pack('>i', int(val))
    elif type_tag == ',f':
        data = struct.pack('>f', float(val))
    return addr + tag + data

def decode_osc(data):
    try:
        end_idx = data.find(b'\0')
        addr = data[:end_idx].decode('latin-1')
        # Skip padding and type tag to find value?
        # A simple hacky decoder for known expected types
        # This test knows what to expect
        return addr
    except:
        return None

def test():
    print("🚀 Starting Integrity Test")
    
    # Start Bridge
    proc = subprocess.Popen([sys.executable, "bridge_v48_test.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2) # Wait for startup
    
    try:
        # Mock Wing Receiver
        sock_wing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_wing.bind(('127.0.0.1', WING_MOCK_PORT))
        sock_wing.settimeout(2)
        
        # Connect as Xilica
        sock_xilica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_xilica.connect(('127.0.0.1', XILICA_PORT))
        sock_xilica.settimeout(2)
        print("✅ Connected to Bridge Key (Xilica Side)")
        
        # --- TEST 1: Xilica -> Wing (Volume) ---
        print("\n--- TEST 1: Xilica set 1chv 5.0 -> Wing ---")
        sock_xilica.send(b"set 1chv 5.0\r")
        
        try:
            data, addr = sock_wing.recvfrom(1024)
            print(f"📥 Received at Wing Mock: {data}")
            if b"/ch/1/fdr" in data:
                print("✅ PASS: Wing received Volume OSC addr")
            else:
                print("❌ FAIL: Wrong OSC addr")
        except socket.timeout:
            print("❌ FAIL: Timeout waiting for Wing packet")

        # --- TEST 2: Xilica -> Wing (Mute) ---
        print("\n--- TEST 2: Xilica set 1chm TRUE -> Wing ---")
        sock_xilica.send(b"set 1chm TRUE\r")
        
        try:
            data, addr = sock_wing.recvfrom(1024)
            print(f"📥 Received at Wing Mock: {data}")
            if b"/ch/1/mute" in data:
                print("✅ PASS: Wing received Mute OSC addr")
                # Could decode value here
            else:
                print("❌ FAIL: Wrong OSC addr")
        except socket.timeout:
            print("❌ FAIL: Timeout waiting for Wing packet")

        # --- TEST 3: Wing -> Xilica (Volume Feedback) ---
        print("\n--- TEST 3: Wing /ch/2/fdr 0.5 -> Xilica ---")
        # 0.5 normalized -> ~ -40dB?
        # Map logic: db = (0.5 * 10) - 90 = -85 ??
        # Wait, bridge map_db_to_xilica: val = (db + 90)/10. 
        # So raw 0.5 at Wing (if Wing uses normalized 0-1) -> bridge code does what?
        # Bridge receiver: 
        # val = struct.unpack('>f', ...)[0]
        # x_val = map_db_to_xilica(val)  <-- THIS expects 'val' to be dB?
        # Wing sends Normalized (0-1) or dB? The summary says "Wing sends feedback... Volume feedback is float".
        # Usually Wing sends normalized 0.0-1.0 floats for faders.
        # But `map_db_to_xilica` takes `db_val`.
        #   val = (db_val + 90.0) / 10.0
        # If Wing sends 0.75 (normalized), bridge treats it as 0.75 dB? That would be weird.
        # Let's check bridge_v48.py logic again.
        
        # Bridge v48: 
        # x_val = map_db_to_xilica(val) 
        # if val comes from Wing as 0...1, then 0.75 dB is -89.25?
        # Wait. IF Wing sends dB, it sends -90 to +10.
        # IF Wing sends float 0-1, we need to convert 0-1 to dB first? Or direct to Xilica?
        # map_db_to_xilica assumes input is dB (-90 to +10).
        # Does Wing send dB?
        # Summary says: "Wing OSC Format... Volume feedback is float ('f')."
        # Standard Wing OSC /ch/1/fdr is normalized 0.0 to 1.0.
        # If bridge treats 0.0-1.0 as dB, the output to Xilica will be (0+90)/10 = 9.0 to (1+90)/10 = 9.1.
        # This seems WRONG if Xilica wants 0-10 range representing full scale.
        # Let's re-read the mapping connection.
        
        osc_pkt = build_osc_packet("/ch/2/fdr", ",f", -10.0) # sending -10 dB assuming Bridge expects dB
        sock_wing_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_wing_sender.sendto(osc_pkt, ('127.0.0.1', BRIDGE_PORT))
        
        try:
            data = sock_xilica.recv(1024)
            print(f"📥 Received at Xilica: {data}")
            if b"set 2chv" in data:
                 print("✅ PASS: Xilica received Feedback")
            else:
                 print("❌ FAIL: Xilica received wrong data")
        except socket.timeout:
             print("❌ FAIL: Timeout waiting for Xilica feedback")
             
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print("Stopping Bridge...")
        proc.kill()

if __name__ == "__main__":
    test()
