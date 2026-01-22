from pythonosc import udp_client
import time

BRIDGE_IP = "127.0.0.1"
BRIDGE_PORT = 50000

client = udp_client.SimpleUDPClient(BRIDGE_IP, BRIDGE_PORT)

print("Simulating Wing...")

# Send CH1 Fader update
print("Sending /ch/01/fader 0.75 (approx -12.5dB)")
client.send_message("/ch/01/fader", 0.75)
time.sleep(1)

# Send CH2 Mute update
print("Sending /ch/02/mute 0 (Unmute)")
client.send_message("/ch/02/mute", 0)
time.sleep(1)

# Send Main Vol update
print("Sending /main/st/mix/fader 0.8")
client.send_message("/main/st/mix/fader", 0.8)
time.sleep(1)

# Send Main Mute update (Wing logic: 1=On, 0=Off. Bridge logic: Main Mute 1 -> Wing On 0)
# So sending Wing On 1 means Unmuted in Xilica (Mute 0)
print("Sending /main/st/mix/on 1 (Unmuted)")
client.send_message("/main/st/mix/on", 1)
