from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import time

# Configuration
WING_IP = "192.168.1.11"
WING_PORT = 2223        # Default Wing OSC Port
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 50005     # Port to listen for replies

def print_handler(address, *args):
    print(f"Captured OSC: {address} {args}")

def start_server():
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(print_handler)
    
    server = BlockingOSCUDPServer((LISTEN_IP, LISTEN_PORT), dispatcher)
    print(f"Listening for OSC on {LISTEN_PORT}...")
    server.serve_forever()

if __name__ == "__main__":
    # Start Listener Server in Background
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Client to send subscription request
    client = SimpleUDPClient(WING_IP, WING_PORT)
    
    print(f"Sending subscription request to {WING_IP}:{WING_PORT}...")
    
    # Try multiple subscription commands to be safe
    # /xremote is standard for X32/Wing to send UI updates to the sender
    client.send_message("/xremote", []) 
    client.send_message("/xinfo", [])
    
    # Also tried sending to specific port?
    # Usually /xremote makes the console reply to the source IP/Port of the packet.
    
    print("\nXXX NOW MOVE A FADER ON THE MIXER XXX")
    print("Waiting for messages (Ctrl+C to stop)...")
    
    start_time = time.time()
    msg_count = 0
    # Monkey patch the handler to count
    original_handler = print_handler
    def counting_handler(addr, *args):
        global msg_count
        print(f"Captured OSC: {addr} {args}")
        # Identify interesting messages
        msg_count += 1
        
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(counting_handler)
    
    # Restart server with new dispatcher? No, complicate. 
    # Just checking logic. 
    # Let's just loop and print manually? SimpleUDPClient is for sending.
    # Server is in thread. 
    
    # Let's just limit the wait time in main thread
    for i in range(60): # 60 * 1 = 60 seconds max
        if time.time() - start_time > 60: break
        # We can't easily check msg_count from thread without simple object. 
        # But user will move fader.
        # Let's just run for 15 seconds then exit.
        time.sleep(1)
        client.send_message("/xremote", [])
        
    print("Timeout reached. Exiting.")
    import os
    os._exit(0)
