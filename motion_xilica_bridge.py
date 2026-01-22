import socket
from gpiozero import PWMLED, MotionSensor
from signal import pause
import sys

# --- Configuration ---
# Xilica Target
xillica_ip = "192.168.1.30"
xillica_port = 10007

# GPIO Pins
led_0 = PWMLED(5)   # Indicator 1
led_1 = PWMLED(21)  # Indicator 2
pir = MotionSensor(18)

# Commands
# MUTE_COMMAND: Sets Volume 'v1' to -100.0 dB (Silence)
MUTE_COMMAND = "SET v1 -100.0\r\n" 
# UNMUTE_COMMAND: Sets Volume 'v1' to 15.0 dB
UNMUTE_COMMAND = "SET v1 15.0\r\n" 

def send_presset_to_xillica(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((xillica_ip, xillica_port))
            s.sendall(command.encode())
            # Optional: Set a timeout for receive to prevent blocking
            s.settimeout(2.0)
            try:
                response = s.recv(1024)
                print(f"xlillcia 응답: {response.decode().strip()}")
            except socket.timeout:
                print("Xilica 응답 없음 (Timeout)")
    except Exception as e:
        print(f"프리셋 전송 오류:{e}")

def motion_detected():
    print("동작이 감지됨 - MUTE 실행")
    led_0.on()
    led_1.off()
    send_presset_to_xillica(MUTE_COMMAND)

def motion_stopped():
    print("동작 없음 - UNMUTE 실행")
    led_0.off()
    led_1.on()
    send_presset_to_xillica(UNMUTE_COMMAND)

# --- Logic Hooks ---
pir.when_motion = motion_detected
pir.when_no_motion = motion_stopped

print("Motion Sensor Bridge Started... Waiting for events.")
pause()
