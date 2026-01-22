import socket
from gpiozero import PWMLED, MotionSensor
from signal import pause
import sys

# --- Configuration ---
xillica_ip = "192.168.1.30"
xillica_port = 10007

# GPIO Pins
led_0 = PWMLED(5)   # Indicator 1
led_1 = PWMLED(21)  # Indicator 2
pir = MotionSensor(18)

# --- Xilica Component Names ---
# Xilica Designer의 Component Name과 일치시켜 주세요.
MUTE_LATCH_NAME = "mute_btn" 
VOLUME_NUMERIC_NAME = "vol_level" 

# --- Volume Levels (Scale 1 ~ 10) ---
# 사용자의 요청에 따라 1~10 사이의 값으로 설정합니다.
VOL_MIN = 1    # 동작 감지 시 (최소 볼륨/조용함)
VOL_NORMAL = 8 # 동작 없을 시 (기본 볼륨/소리 큼) - 필요에 따라 1~10 사이 조절

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
    print(f"🎬 Motion Detected - Muting & Volume to {VOL_MIN}")
    led_0.on()
    led_1.off()
    
    # 1. Mute ON (Latch Button -> 1)
    send_xilica_cmd(f"SETRAW {MUTE_LATCH_NAME} 1")
    
    # 2. Volume to MIN (Numeric -> 1)
    send_xilica_cmd(f"SET {VOLUME_NUMERIC_NAME} {VOL_MIN}")

def motion_stopped():
    print(f"🛑 Motion Stopped - Unmuting & Volume to {VOL_NORMAL}")
    led_0.off()
    led_1.on()

    # 1. Mute OFF (Latch Button -> 0)
    send_xilica_cmd(f"SETRAW {MUTE_LATCH_NAME} 0")
    
    # 2. Volume to NORMAL (Numeric -> 8)
    send_xilica_cmd(f"SET {VOLUME_NUMERIC_NAME} {VOL_NORMAL}")

# --- Hooks ---
pir.when_motion = motion_detected
pir.when_no_motion = motion_stopped

print(f"🚀 Xilica Bridge V3 (Numeric 1-10) Started.")
print(f"Logic: Motion -> Vol {VOL_MIN} | No Motion -> Vol {VOL_NORMAL}")
pause()
