import socket
from gpiozero import PWMLED, MotionSensor
from signal import pause
import sys

# --- Configuration ---
xillica_ip = "192.168.1.30"
xillica_port = 10007

# GPIO Pins
led_0 = PWMLED(5)
led_1 = PWMLED(21)
pir = MotionSensor(18)

# --- Xilica Component Names (User defined) ---
# Xilica Designer에서 설정한 "Component Name"을 정확히 입력하세요.
# 예: Latch Button -> "mute_btn", Numeric -> "vol_num"
MUTE_LATCH_NAME = "mute_btn" 
VOLUME_NUMERIC_NAME = "vol_level" 

# --- Control Logic ---
# Latch Button: Use SETRAW for reliable toggle control
# Numeric: Use SET followed by the value

def send_xilica_cmd(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((xillica_ip, xillica_port))
            # Critical: Xilica expects \r (CR) termination
            full_cmd = command.strip() + "\r"
            s.sendall(full_cmd.encode())
            print(f"📤 Sent: {full_cmd.strip()}")
            
            try:
                response = s.recv(1024)
                print(f"📥 Response: {response.decode().strip()}")
            except socket.timeout:
                pass
    except Exception as e:
        print(f"❌ Xilica Error: {e}")

def motion_detected():
    print("🎬 Motion Detected - Enabling Privacy/Mute")
    led_0.on()
    led_1.off()
    
    # 1. Mute ON (Latch Button -> 1/ON)
    # SETRAW is recommended for Latch Buttons in Xilica
    send_xilica_cmd(f"SETRAW {MUTE_LATCH_NAME} 1")
    
    # 2. Volume to Min (Numeric -> 0)
    # Adjust value '0' if your Numeric logic differs
    send_xilica_cmd(f"SET {VOLUME_NUMERIC_NAME} 0")

def motion_stopped():
    print("🛑 Motion Stopped - Restoring Volume")
    led_0.off()
    led_1.on()

    # 1. Mute OFF (Latch Button -> 0/OFF)
    send_xilica_cmd(f"SETRAW {MUTE_LATCH_NAME} 0")
    
    # 2. Volume to Normal (Numeric -> 75 or desired level)
    # Adjust '75' to your standard level
    send_xilica_cmd(f"SET {VOLUME_NUMERIC_NAME} 75")

# --- Hooks ---
pir.when_motion = motion_detected
pir.when_no_motion = motion_stopped

print(f"🚀 Xilica Bridge V2 (Latch/Numeric) Started.")
print(f"Target: {xillica_ip}:{xillica_port}")
pause()
