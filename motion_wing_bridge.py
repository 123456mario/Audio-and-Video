from gpiozero import PWMLED, MotionSensor
from signal import pause
from pythonosc import udp_client
import sys

# --- Configuration ---
# Behringer Wing Target
WING_IP = "192.168.1.11" # Standard Wing IP
WING_PORT = 2223         # Standard Wing Port

# Target Channel to Control
TARGET_CHANNEL = 1       # Channel 1

# GPIO Pins
led_0 = PWMLED(5)   # Indicator 1 (Red/Muted)
led_1 = PWMLED(21)  # Indicator 2 (Green/Unmuted)
pir = MotionSensor(18)

# OSC Client Setup
client = udp_client.SimpleUDPClient(WING_IP, WING_PORT)

def send_wing_mute(channel, state):
    """
    Sends Mute command to Behringer Wing.
    Path: /ch/{channel}/mute
    Value: 1 (Mute) / 0 (Unmute)
    """
    try:
        osc_path = f"/ch/{channel}/mute"
        osc_value = 1 if state else 0
        
        client.send_message(osc_path, osc_value)
        print(f"📤 Sent to Wing: {osc_path} -> {osc_value}")
        
    except Exception as e:
        print(f"❌ Wing send error: {e}")

def motion_detected():
    print("🎬 동작 감지됨 - MUTE (조용히)")
    led_0.on()
    led_1.off()
    
    # Motion Logic: MUTE ON (Value 1)
    send_wing_mute(TARGET_CHANNEL, True)

def motion_stopped():
    print("🛑 동작 없음 - UNMUTE (소리 출력)")
    led_0.off()
    led_1.on()

    # Motion Stopped Logic: MUTE OFF (Value 0)
    send_wing_mute(TARGET_CHANNEL, False)

# --- Logic Hooks ---
pir.when_motion = motion_detected
pir.when_no_motion = motion_stopped

print(f"🚀 Wing Motion Bridge Started.")
print(f"Target: {WING_IP}:{WING_PORT} | Channel: {TARGET_CHANNEL}")
pause()
