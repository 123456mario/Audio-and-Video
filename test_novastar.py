import socket
import time
import argparse

# DEFAULT CONFIGURATION
# ---------------------
# Replace with your actual Novastar IP
DEFAULT_IP = "192.168.1.60" 
DEFAULT_PORT = 15200 # Found to be 15200 in previous testing
TIMEOUT = 3.0

# NOVASTAR COMMANDS
# -----------------
# 1. READ MODE ID (Ping / Heartbeat)
# Should return "aa 55 ..." without changing screen
CMD_PING = bytes([
    0x55, 0xaa, 0x00, 0x00, 0xfe, 0x00, 0x00, 0x00, 
    0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 
    0x00, 0x00, 0x57, 0x56
])

# 2. BLACK SCREEN (Turn Off Display Content)
CMD_BLACK = bytes([
    0x55, 0xaa, 0x00, 0x00, 0xfe, 0xff, 0x01, 0xff, 
    0xff, 0xff, 0x01, 0x00, 0x00, 0x01, 0x00, 0x02, 
    0x01, 0x00, 0xff, 0x54, 0x5b
])

# 3. NORMAL DISPLAY (Turn On Display Content)
CMD_NORMAL = bytes([
    0x55, 0xaa, 0x00, 0x00, 0xfe, 0xff, 0x01, 0xff, 
    0xff, 0xff, 0x01, 0x00, 0x00, 0x01, 0x00, 0x02, 
    0x01, 0x00, 0x00, 0x55, 0x5a
])

def send_command(ip, port, command, cmd_name):
    print(f"\n--- Sending {cmd_name} ---")
    print(f"Target: {ip}:{port}")
    print(f"Hex: {' '.join([f'{b:02x}' for b in command])}")
    
    try:
        # Novastar usually uses TCP, but sometimes UDP. Trying TCP first.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            s.connect((ip, port))
            s.sendall(command)
            
            print("Command sent. Waiting for response...")
            try:
                data = s.recv(1024)
                if data:
                    hex_resp = ' '.join([f'{b:02x}' for b in data])
                    print(f"Response Received: {hex_resp}")
                    if data.startswith(b'\xaa\x55'):
                        print("SUCCESS: Valid Novastar acknowledgment header (AA 55).")
                    else:
                        print("WARNING: Response header mismatch (Expected AA 55).")
                else:
                    print("No data received.")
            except socket.timeout:
                print("Timed out waiting for response.")
                
    print(f"Connection Error: {e}")

def start_server(port):
    print(f"\n--- Starting Novastar Mock Server ---")
    print(f"Listening on 0.0.0.0:{port}")
    print("Use this mode to check what Xilica is actually sending.")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('0.0.0.0', port))
            s.listen(1)
            print("Waiting for connection...")
            
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            print("Connection closed.")
                            break
                        hex_data = ' '.join([f'{b:02x}' for b in data])
                        print(f"RECEIVED DATA: {hex_data}")
                        
                        # Respond with Ack if it looks like a Novastar command
                        # Novastar usually expects an Ack to close the transaction gracefully
                        ack = bytes([0xaa, 0x55]) # Simple Ack? Or mirror?
                        # Usually the device responds with aa 55 ... 
                        # We will just print for now.
                        
                print("Waiting for next connection...")
                
        except Exception as e:
            print(f"Server Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Novastar LED Display Commands")
    parser.add_argument("--ip", default=DEFAULT_IP, help="IP address of Novastar Controller (Target for Client Mode)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port (Default: 5200)")
    parser.add_argument("--cmd", choices=["ping", "black", "normal"], default="ping", help="Command to send (Client Mode)")
    parser.add_argument("--listen", action="store_true", help="Run in Server Mode to listen for Xilica triggers")
    
    args = parser.parse_args()
    
    if args.listen:
        start_server(args.port)
    else:
        cmd_bytes = CMD_PING
        if args.cmd == "black": cmd_bytes = CMD_BLACK
        elif args.cmd == "normal": cmd_bytes = CMD_NORMAL
        
        send_command(args.ip, args.port, cmd_bytes, args.cmd.upper())
