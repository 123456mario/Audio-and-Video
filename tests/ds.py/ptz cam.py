import socket
import requests
from requests.auth import HTTPDigestAuth
import threading
import time
import datetime
import subprocess
import signal
import sys
import platform  # For OS check

# PTZ Camera IPs and Credentials
CAM1_IP = "192.168.1.30"
CAM2_IP = "192.168.1.31"
USERNAME = "admin"
PASSWORD = "1234"

PORT = 10001

# Direction to CGI command mapping
directions = {
    "RIGHT": "%23PTS9950",
    "LEFT": "%23PTS0150",
    "UP": "%23PTS5099",
    "DOWN": "%23PTS5001",
    "STOP": "%23PTS5050",
    "HOME": "%23APC7FFF7FFF"
}

# State management
active_movements = {"CAM1": None, "CAM2": None}
last_on_time = {"CAM1": 0, "CAM2": 0}  # 1.5s duplicate prevention
movement_lock = threading.Lock()

def log_message(message, addr=None):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    addr_str = f" from {addr}" if addr else ""
    print(f"[{timestamp}]{addr_str} {message}")

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

def configure_keepalive(sock):
    """Cross-platform keepalive configuration"""
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        os_name = platform.system()
        log_message(f"Keepalive configured for {os_name}")
        if os_name == 'Linux':
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)  # Linux-specific
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
            log_message("Advanced Linux keepalive options applied")
        else:
            log_message("Basic keepalive applied (macOS/Windows - advanced options not supported)")
    except Exception as e:
        log_message(f"[WARNING] Keepalive setup error: {e} (using basic SO_KEEPALIVE)")

def control_ptz(cam_ip, command):
    url = f"http://{cam_ip}/cgi-bin/aw_ptz?cmd={command}&res=1"
    log_message(f"Sending URL to {cam_ip}: {url}")
    start_time = time.time()
    try:
        response = requests.get(url, auth=HTTPDigestAuth(USERNAME, PASSWORD), timeout=10)
        elapsed = time.time() - start_time
        log_message(f"[Response] Status Code: {response.status_code} - Text: {response.text} (elapsed: {elapsed:.3f}s)")
        if response.status_code == 200:
            log_message(f"[SUCCESS] Sent to {cam_ip}: {command}")
            return True
        else:
            log_message(f"[ERROR] Sending to {cam_ip}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        log_message(f"[REQUEST ERROR] to {cam_ip}: {e} (elapsed: {elapsed:.3f}s)")
        return False

def continuous_movement(cam_id, direction):
    cam_ip = CAM1_IP if cam_id == "CAM1" else CAM2_IP
    log_message(f"Starting continuous movement for {cam_id} in direction {direction}")
    while active_movements[cam_id] == direction:
        if control_ptz(cam_ip, directions[direction]):
            time.sleep(1.0)  # 1.0s interval to reduce load
    log_message(f"Stopped continuous movement for {cam_id}")

def handle_connection(conn, addr):
    log_message(f"New persistent connection from {addr} - Keeping open with keepalive")
    configure_keepalive(conn)
    conn.settimeout(10.0)
    last_activity = time.time()
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                log_message(f"Connection from {addr} closed by client (no data)")
                break
            last_activity = time.time()
            cmd = data.decode('ascii').strip()
            log_message(f"Raw data: {data}")
            log_message(f"Received command: {cmd}")
            parts = cmd.split()
            if len(parts) == 3:
                cam_id, direction, state = parts
                # Validity check
                if cam_id in ["CAM1", "CAM2"] and direction in directions and state in ["ON", "OFF"]:
                    log_message(f"Valid: {cam_id} {direction} {state} (active: {active_movements[cam_id]})")
                    current_time = time.time()
                    try:
                        with movement_lock:
                            if state == "ON":
                                # Enhanced duplicate prevention
                                if current_time - last_on_time[cam_id] < 1.5:
                                    log_message(f"[DUPLICATE PREVENTED] Ignored ON for {cam_id} {direction} (too soon)")
                                    conn.send(b"OK\r\n")
                                else:
                                    last_on_time[cam_id] = current_time
                                    # Strict double movement prevention
                                    if active_movements[cam_id] == direction:
                                        log_message(f"[DOUBLE MOVEMENT PREVENTED] {cam_id} {direction} already active, skipping")
                                        conn.send(b"OK\r\n")
                                    else:
                                        if direction == "HOME":
                                            log_message(f"Processing HOME for {cam_id}")
                                            control_ptz(CAM1_IP if cam_id == "CAM1" else CAM2_IP, directions["HOME"])
                                        else:
                                            active_movements[cam_id] = direction
                                            threading.Thread(target=continuous_movement, args=(cam_id, direction), daemon=True).start()
                                        conn.send(b"OK\r\n")
                            elif state == "OFF":
                                active_movements[cam_id] = None
                                cam_ip = CAM1_IP if cam_id == "CAM1" else CAM2_IP
                                log_message(f"Processing OFF for {cam_id}, sending STOP")
                                control_ptz(cam_ip, directions["STOP"])
                                conn.send(b"OK\r\n")
                    except Exception as lock_e:
                        log_message(f"[LOCK ERROR]: {lock_e}")
                        conn.send(b"ERR\r\n")
                else:
                    log_message(f"[WARNING] Invalid command: {cmd}")
                    conn.send(b"ERR\r\n")
            elif cmd.strip() == "STOP":
                log_message(f"Global stop from {addr}")
                with movement_lock:
                    active_movements["CAM1"] = None
                    active_movements["CAM2"] = None
                    control_ptz(CAM1_IP, directions["STOP"])
                    control_ptz(CAM2_IP, directions["STOP"])
                conn.send(b"OK\r\n")
            else:
                log_message(f"[WARNING] Invalid format from {addr}: {cmd}")
                conn.send(b"ERR\r\n")
            # Heartbeat for keepalive
            if time.time() - last_activity > 5.0:
                conn.send(b"PING\r\n")
                last_activity = time.time()
        except socket.timeout:
            if time.time() - last_activity > 30.0:
                log_message(f"Closing idle connection from {addr} (30s timeout)")
                break
            continue
        except Exception as e:
            log_message(f"[CONNECTION ERROR] from {addr}: {e}")
            break
    conn.close()
    log_message(f"Connection from {addr} closed")

# Free port if occupied
check_and_free_port(PORT)

# TCP Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
configure_keepalive(server)  # Apply keepalive to server socket
server.settimeout(5.0)
try:
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    log_message(f"PTZ TCP Server listening on port {PORT} with cross-platform keepalive")
except OSError as e:
    log_message(f"[BIND ERROR] Port {PORT}: {e}")
    sys.exit(1)

def signal_handler(sig, frame):
    log_message("Shutdown signal - closing server")
    server.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        log_message(f"Waiting for connection on port {PORT}...")
        conn, addr = server.accept()
        log_message(f"Connection from: {addr}")
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()
    except socket.timeout:
        log_message(f"Accept timeout - server listening")
        continue
    except Exception as e:
        log_message(f"[SERVER ERROR]: {e}")
        import traceback
        traceback.print_exc()
    time.sleep(0.1)
