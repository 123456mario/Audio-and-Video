from pythonosc import dispatcher
from pythonosc import osc_server
import time

def print_handler(address, *args):
    print(f"[Virtual Wing] Received: {address} : {args}")

def start_server():
    disp = dispatcher.Dispatcher()
    disp.map("*", print_handler)
    
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 2223), disp)
    print("Virtual Wing OSC Server Listening on 127.0.0.1:2223...")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
