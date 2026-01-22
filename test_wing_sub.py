import time
import threading
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

WING_IP = "192.168.1.11"
WING_PORT = 2223
LISTEN_PORT = 0  # Dynamic port

def print_handler(addr, *args):
    print(f"🎉 RECEIVED! {addr} {args}")

def run_server(server):
    print(f"👂 Listening on port {server.server_address[1]}...")
    server.serve_forever()

# 1. Start Listening Server
dispatcher = Dispatcher()
dispatcher.set_default_handler(print_handler)
server = BlockingOSCUDPServer(("0.0.0.0", LISTEN_PORT), dispatcher)
listen_port = server.server_address[1]

t = threading.Thread(target=run_server, args=(server,), daemon=True)
t.start()

# 2. Client to send Commands
client = SimpleUDPClient(WING_IP, WING_PORT)

commands_to_try = [
    ("/xremote", []),
    ("/subscribe", ["/ch/1/fdr", 100]), # Path, Interval
    ("/batch/subscribe", ["/ch/1/fdr", 1]),
    ("/info", []),
    ("/prefs/xremote", [1]),
    ("/ch/1/fdr", []) # Just querying status (not sub)
]

print(f"🎯 Targeting Wing at {WING_IP}:{WING_PORT} from port {listen_port}")
print("🚀 Sending subscription attempts... PLEASE MOVE FADER 1 NOW!")

try:
    for cmd, args in commands_to_try:
        print(f"➡️ Sending: {cmd} {args}")
        client.send_message(cmd, args)
        time.sleep(2)
        
    print("⏳ Waiting 10s for any delayed response...")
    time.sleep(10)

except KeyboardInterrupt:
    pass
print("Done.")
