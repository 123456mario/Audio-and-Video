import socket
import time
import sys

# Configuration
NOVASTAR_IP = "192.168.1.60"
NOVASTAR_PORT = 15200      # Validated Control Port

# Command Database
# PING Command for Keepalive (Read Mode ID)
PING_CMD = bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56")

def log_message(message):
    print(message)
    sys.stdout.flush()

def send_to_novastar_stateless(cmd_bytes):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((NOVASTAR_IP, NOVASTAR_PORT))
        s.send(cmd_bytes)
        s.close()
        return True
    except Exception as e:
        log_message(f"❌ Connect Failed: {e}")
        return False

def start_heartbeat():
    while True:
        try:
            send_to_novastar_stateless(PING_CMD)
            log_message("💓 Keepalive Ping Sent")
            time.sleep(10)
        except Exception as e:
            log_message(f"❌ Heartbeat Error: {e}")
            time.sleep(10)

def main():
    log_message(f"🚀 Novastar Keepalive Service Starting...")
    log_message(f"   Target: {NOVASTAR_IP}:{NOVASTAR_PORT}")
    log_message(f"   Interval: 10 seconds")
    
    # Start loop
    # start_heartbeat() # DISABLED for Xilica Testing
    log_message("⏸️ Keepalive PAUSED for Xilica Testing")
    while True:
        time.sleep(10) # Just sleep to keep process alive if needed, or it can exit. Keeping alive for easy re-enable.

if __name__ == "__main__":
    main()
