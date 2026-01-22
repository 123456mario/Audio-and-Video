from pythonosc import dispatcher, osc_server
import threading

def print_handler(address, *args):
    print(f"Wing Received: {address} {args}")

disp = dispatcher.Dispatcher()
disp.set_default_handler(print_handler)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 2223), disp)
print("Wing Mock Server listening on 2223...")
server.serve_forever()
