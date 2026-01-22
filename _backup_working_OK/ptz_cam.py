import socket
import requests
from requests.auth import HTTPDigestAuth
import threading
import time
import datetime
import subprocess
import signal
import sys
import platform
import queue

# PTZ Camera IPs and Credentials
CAM1_IP = "192.168.1.30"
CAM2_IP = "192.168.1.31"
USERNAME = "admin"
PASSWORD = "1234"

PORT = 10001
UDP_PORT_CAM = 1259

# Accurate direction mapping based on PTS protocol
def get_pts_command(direction):
    d = direction.upper()
    # Speed Scale: 01 (Max Left/Down) <-> 50 (Stop) <-> 99 (Max Right/Up)
    
    # FIXED: Standard Direction Logic (Right=Right, Left=Left) based on latest feedback
    if d == "RIGHT": return "#PTS9950"  # Pan Right (Max)
    if d == "LEFT":  return "#PTS0150"  # Pan Left (Max)
    if d == "UP":    return "#PTS5099"  # Max Up
    if d == "DOWN":  return "#PTS5001"  # Max Down
    if d == "STOP":  return "#PTS5050"  # All Stop
    
    # Fine controls (Standard mapping)
    if d == "REL_RIGHT": return "#PTS9950" 
    if d == "REL_LEFT":  return "#PTS0150" 
    if d == "REL_UP":    return "#PTS5099"
    if d == "REL_DOWN":  return "#PTS5001"
    
    # Zoom Control (Standard & REL)
    if d == "ZOOMIN" or d == "REL_ZOOMIN":   return "#Z95"
    if d == "ZOOMOUT" or d == "REL_ZOOMOUT": return "#Z05"
    if d == "ZOOMSTOP": return "#Z50"
    
    # Home Position -> Changed to use PRESET 1
    # User can save their desired "Home" to Preset 1 on the camera.
    if d == "HOME":     return "#R01"
    
    return None

# State management
movement_state = {"CAM1": None, "CAM2": None}
last_on_time = {"CAM1": 0, "CAM2": 0}
command_queues = {"CAM1": queue.Queue(), "CAM2": queue.Queue()}
active_mode = {"CAM1": "MANUAL", "CAM2": "MANUAL"} 
preset_lock_until = {"CAM1": 0, "CAM2": 0} # Timestamp to ignore STOPs

def log_message(message, addr=None):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    addr_str = f" from {addr}" if addr else ""
    print(f"[{timestamp}]{addr_str} {message}")
    sys.stdout.flush() # Force flush

class NoDelayAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        import socket
        kwargs['socket_options'] = [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        ]
        return super(NoDelayAdapter, self).init_poolmanager(*args, **kwargs)

def create_camera_session(cam_ip):
    s = requests.Session()
    s.auth = HTTPDigestAuth(USERNAME, PASSWORD)
    adapter = NoDelayAdapter(pool_connections=20, pool_maxsize=20)
    s.mount('http://', adapter)
    return s

cam_sessions = {
    CAM1_IP: create_camera_session(CAM1_IP),
    CAM2_IP: create_camera_session(CAM2_IP)
}

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

def control_ptz_udp(cam_ip, command):
    msg = b"\x02" + command.encode('ascii') + b"\x03"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        sock.sendto(msg, (cam_ip, UDP_PORT_CAM))
        return True
    except Exception as e:
        log_message(f"[UDP ERROR] {command} -> {cam_ip} | {e}")
        return False

def control_ptz_http(cam_ip, command, is_warming=False, queue_time=None):
    base_url = f"http://{cam_ip}/cgi-bin/aw_ptz"
    params = {
        "cmd": command,
        "res": "1"
    }
    
    timeout = 1.0 if not is_warming else 0.3
    session = cam_sessions.get(cam_ip)

    if not session:
        log_message(f"[ERROR] No session for {cam_ip}")
        return False

    try:
        start_time = time.time()
        internal_delay = (start_time - queue_time) * 1000 if queue_time else 0
        
        # Log BEFORE sending to verify execution flow
        if not is_warming:
            pass # Skipping pre-log to avoid clutter, will log result
        
        response = session.get(base_url, params=params, timeout=timeout)
        elapsed = (time.time() - start_time) * 1000
        
        type_str = "[WARM]" if is_warming else "[HTTP]"
        if not is_warming:
            body_sample = response.text.strip()[:20] 
            log_message(f"{type_str} {command} -> {cam_ip} | Status: {response.status_code} | Body: {body_sample} | Net: {elapsed:.1f}ms")
        return response.status_code == 200
    except Exception as e:
        if not is_warming:
            log_message(f"[HTTP ERROR] {command} -> {cam_ip} | {e}")
        return False

def camera_worker(cam_id):
    cam_ip = CAM1_IP if cam_id == "CAM1" else CAM2_IP
    log_message(f"[WORKER] {cam_id} thread started")
    while True:
        try:
            if command_queues[cam_id].empty():
                time.sleep(0.01)
                continue
            
            msg = command_queues[cam_id].get(timeout=0.1)
            if msg is None: break
            
            cmd_text, queue_time = msg
            
            # Parse Xilica Command
            parts = cmd_text.split()
            if len(parts) < 3: continue
            
            cam_name = parts[0]
            direction = parts[1]
            action = parts[2]
            
            cam_ip = CAM_IPS.get(cam_name)
            if not cam_ip: continue
            
            # 1. STOP Logic (Falling Edge)
            # IGNORE STOP if we are in PRESET mode (let it finish)
            if action == "OFF":
                # Check Lock Timer
                if time.time() < preset_lock_until[cam_id]:
                    # Ignore STOP because we are moving to preset
                    command_queues[cam_id].task_done()
                    continue

                if active_mode[cam_id] == "MANUAL":
                    if not direction.startswith("REL_") or "ZOOM" in direction:
                        command = get_pts_command("STOP")
                        zoom_stop = get_pts_command("ZOOMSTOP")
                        
                        control_ptz_udp(cam_ip, command)
                        control_ptz_udp(cam_ip, zoom_stop)
                        
                        control_ptz_http(cam_ip, command)
                        control_ptz_http(cam_ip, zoom_stop)
                command_queues[cam_id].task_done()
                continue

            # 2. START Logic (Rising Edge)
            raw_cmd = get_pts_command(direction)
            if not raw_cmd: continue
            
            # Determine Mode & Set Lock
            if direction == "HOME":
                active_mode[cam_id] = "PRESET"
                preset_lock_until[cam_id] = time.time() + 5.0 # Lock stops for 5s
            else:
                active_mode[cam_id] = "MANUAL"
                preset_lock_until[cam_id] = 0 # Unlock immediately for manual moves

            if direction.startswith("REL_") and "ZOOM" not in direction:
                # PRECISE PULSE LOGIC (Pan/Tilt Only)
                # [OPTIMIZATION] Only use UDP for the "Start" kick to avoid HTTP blocking latency
                control_ptz_udp(cam_ip, raw_cmd)
                
                # FIXED: Enable HTTP backup for Start command (in case UDP fails)
                control_ptz_http(cam_ip, raw_cmd, queue_time=queue_time)
                
                # ADJUST PULSE DURATION BY AXIS
                if "UP" in direction or "DOWN" in direction:
                    time.sleep(0.1) # INCREASED from 0.02
                else:
                    time.sleep(0.1) # INCREASED from 0.05
                
                # Send STOP
                stop_cmd = get_pts_command("STOP")
                control_ptz_udp(cam_ip, stop_cmd)
                control_ptz_http(cam_ip, stop_cmd)
                
            else:
                # Continuous Movement (Zoom & Speed Holds & Presets)
                control_ptz_udp(cam_ip, raw_cmd)
                control_ptz_http(cam_ip, raw_cmd, queue_time=queue_time)
            
            command_queues[cam_id].task_done()
                
        except Exception as e:
            log_message(f"[SERVER ERROR]: {e}")
            time.sleep(1.0)

def keep_warm():
    while True:
        for cam_id, cam_ip in zip(["CAM1", "CAM2"], [CAM1_IP, CAM2_IP]):
            if movement_state[cam_id] is None:
                control_ptz_http(cam_ip, "#O", is_warming=True) 
        time.sleep(8)

def safety_watchdog():
    while True:
        now = time.time()
        for cam_id in ["CAM1", "CAM2"]:
            if movement_state[cam_id] and (now - last_on_time[cam_id] > 10.0):
                action = movement_state[cam_id]
                log_message(f"[WATCHDOG] Safety stop for {cam_id} (Active: {action})")
                movement_state[cam_id] = None
        time.sleep(0.3)

check_and_free_port(PORT)
server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    server_udp.bind(("0.0.0.0", PORT))
    log_message(f"PTZ UDP Input Server listening on port {PORT}")
except OSError as e:
    log_message(f"[BIND ERROR] Port {PORT}: {e}")
    sys.exit(1)

def signal_handler(sig, frame):
    log_message("Shutdown signal - closing server")
    server_udp.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

CAM_IPS = {"CAM1": CAM1_IP, "CAM2": CAM2_IP}

for cam in ["CAM1", "CAM2"]:
    threading.Thread(target=camera_worker, args=(cam,), daemon=True).start()

threading.Thread(target=keep_warm, daemon=True).start()
threading.Thread(target=safety_watchdog, daemon=True).start()

last_heartbeat = time.time()

while True:
    try:
        if time.time() - last_heartbeat > 30:
            log_message("HEARTBEAT: Pi Bridge is alive and listening on Port 10001")
            last_heartbeat = time.time()

        server_udp.settimeout(1.0)
        try:
            data, addr = server_udp.recvfrom(1024)
        except socket.timeout:
            continue
        
        cmd_text = data.decode('ascii', errors='ignore').strip('\x00\r\n\t ')
        if not cmd_text: continue
        
        arrival_time = time.time()
        log_message(f"Xilica In: '{cmd_text}'")
        
        parts = cmd_text.split()
        if len(parts) == 3:
            cam_id = parts[0]
            if cam_id in command_queues:
                if not command_queues[cam_id].full():
                    command_queues[cam_id].put((cmd_text, arrival_time))
                    
    except Exception as e:
        log_message(f"[SERVER ERROR]: {e}")
        time.sleep(1.0)
