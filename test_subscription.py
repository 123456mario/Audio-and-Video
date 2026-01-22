from pythonosc import udp_client
import time

# Bridge OSC Port
IP = "127.0.0.1"
PORT = 50000

client = udp_client.SimpleUDPClient(IP, PORT)

print("Sending /ch/01/fader 0.75 (0dB)...")
client.send_message("/ch/01/fader", 0.75)

time.sleep(1)

print("Sending /ch/01/mute 1 (Muted)...")
client.send_message("/ch/01/mute", 1)
