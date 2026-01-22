import socket
import time
import threading
import subprocess
import sys

# Configuration
LISTEN_IP = "0.0.0.0"      # Listen on all Pi interfaces
LISTEN_PORT = 10008        # Changed to 10008 (Diagnostic Port)
NOVASTAR_IP = "192.168.1.60"
NOVASTAR_PORT = 15200      # Validated Control Port

# Pro Series Checksum Logic
def calc_cmd(payload_hex):
    payload = bytes.fromhex(payload_hex.replace(" ", ""))
    checksum = sum(payload) + 0x5555
    sum_l = checksum & 0xFF
    sum_h = (checksum >> 8) & 0xFF
    return b'\x55\xaa' + payload + bytes([sum_l, sum_h])

# Command Database (Pro Protocol + Checksum Calculated)
BRI_HEADER = "00 00 fe ff 01 ff ff ff 01 00 01 00 00 02 01 00"
PRE_HEADER = "00 00 fe 00 00 00 00 00 01 00 00 01 51 13 01 00"

COMMANDS = {
    "POWER_ON": calc_cmd(BRI_HEADER + " ff"), 
    "POWER_OFF": calc_cmd(BRI_HEADER + " 00"), 
    "BRI_20": calc_cmd(BRI_HEADER + " 33"),
    "BRI_40": calc_cmd(BRI_HEADER + " 66"),
    "BRI_60": calc_cmd(BRI_HEADER + " 99"),
    "BRI_80": calc_cmd(BRI_HEADER + " cc"),
    "BRI_100": calc_cmd(BRI_HEADER + " ff"),
    "PRESET_1": calc_cmd(PRE_HEADER + " 00"),
    "PRESET_2": calc_cmd(PRE_HEADER + " 01"),
    "PRESET_3": calc_cmd(PRE_HEADER + " 02"),
    "PING": bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56")
}

def log_message(message):
    print(message)
    sys.stdout.flush()

def check_and_free_port(port):
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            log_message(f"[WARNING] Port {port} occupied by PIDs: {pids}")
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
            time.sleep(2)
            log_message(f"[INFO] Freed port {port}")
            return True
        return False
    except Exception as e:
        log_message(f"[WARNING] Could not free port {port}: {e}")
        return False

def send_to_novastar_stateless(cmd_bytes):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((NOVASTAR_IP, NOVASTAR_PORT))
        s.send(cmd_bytes)
        s.close()
        log_message(f"✅ Sent to Novastar: {len(cmd_bytes)} bytes")
        return True
    except Exception as e:
        log_message(f"❌ Failed to send to Novastar: {e}")
        return False

def start_udp_server():
    check_and_free_port(LISTEN_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((LISTEN_IP, LISTEN_PORT))
        log_message(f"🚀 UDP Listener Active on {LISTEN_PORT}")
    except Exception as e:
        log_message(f"❌ UDP Bind Error: {e}")
        return

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = data.decode('utf-8', errors='ignore').strip().upper()
            log_message(f"📥 UDP Trigger from {addr}: {msg}")
            
            if msg in COMMANDS:
                send_to_novastar_stateless(COMMANDS[msg])
            else:
                log_message(f"⚠️ Unknown command: {msg}")
        except Exception as e:
            log_message(f"❌ UDP Loop Error: {e}")

def start_heartbeat():
    log_message("💓 Heartbeat Thread Started (Every 10s)")
    while True:
        try:
            time.sleep(10)
            send_to_novastar_stateless(COMMANDS["PING"])
            log_message("💓 PING Sent")
        except Exception as e:
            log_message(f"❌ Heartbeat Error: {e}")
            time.sleep(10)

def main():
    log_message(f"🚀 Novastar Universal Bridge Starting...")
    log_message(f"   Target: {NOVASTAR_IP}:{NOVASTAR_PORT}")
    
    t_udp = threading.Thread(target=start_udp_server)
    t_hb = threading.Thread(target=start_heartbeat)
    
    t_udp.daemon = True
    t_hb.daemon = True
    
    t_udp.start()
    t_hb.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("\nStopping Bridge...")

if __name__ == "__main__":
    main()

def start_tcp_server():
    check_and_free_port(LISTEN_PORT) # Shared port check
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(5)
        log_message(f"🚀 TCP Listener Active on {LISTEN_PORT}")
    except Exception as e:
        log_message(f"❌ TCP Bind Error: {e}")
        return

    while True:
        client, addr = server.accept()
        log_message(f"🔌 TCP Connected: {addr}")
        client_handler = threading.Thread(target=handle_tcp_client, args=(client, addr))
        client_handler.daemon = True
        client_handler.start()

def handle_tcp_client(client_socket, addr):
    try:
        buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            # Simple line-based or packet-based parsing
            # Assuming Xilica sends "POWER_ON\r" or "POWER_ON"
            text_chunk = data.decode('utf-8', errors='ignore')
            buffer += text_chunk
            
            if "\r" in buffer or "\n" in buffer:
                lines = buffer.replace("\r", "\n").split("\n")
                buffer = lines[-1] # Keep incomplete part
                
                for line in lines[:-1]:
                    cmd_str = line.strip().upper()
                    if not cmd_str: continue
                    log_message(f"📥 TCP Command from {addr}: {cmd_str}")
                    
                    if cmd_str in COMMANDS:
                        send_to_novastar_stateless(COMMANDS[cmd_str])
                    else:
                        log_message(f"⚠️ Unknown TCP command: {cmd_str}")
    except Exception as e:
        log_message(f"❌ TCP Client Error {addr}: {e}")
    finally:
        client_socket.close()
        log_message(f"🔌 TCP Disconnected: {addr}")

def main():
    log_message(f"🚀 Novastar Universal Bridge Starting...")
    log_message(f"   Target: {NOVASTAR_IP}:{NOVASTAR_PORT}")
    
    # Start threads
    t_udp = threading.Thread(target=start_udp_server)
    t_tcp = threading.Thread(target=start_tcp_server)
    t_hb = threading.Thread(target=start_heartbeat)
    
    t_udp.daemon = True
    t_tcp.daemon = True
    t_hb.daemon = True
    
    t_udp.start()
    t_tcp.start()
    t_hb.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("\nStopping Bridge...")

