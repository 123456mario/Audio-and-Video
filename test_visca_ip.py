import socket
import time

CAM_IP = "192.168.1.31"  # Testing CAM2
VISCA_PORT = 52381

def send_visca(cmd_hex):
    # Standard VISCA over IP requires a header (not always for all models, but safe)
    # Payload: 81 01 06 01 VV WW 0Y 0Z FF
    # Example Pan Right (Speed 08): 81 01 06 01 08 08 02 03 FF
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending VISCA hex: {cmd_hex} to {CAM_IP}:{VISCA_PORT}")
    sock.sendto(bytes.fromhex(cmd_hex), (CAM_IP, VISCA_PORT))

if __name__ == "__main__":
    print("--- Testing VISCA-over-IP (Port 52381) ---")
    # Pan Right (Speed 08, 08): 81 01 06 01 08 08 02 03 FF
    send_visca("8101060108080203FF")
    time.sleep(1)
    # Stop: 81 01 06 01 00 00 03 03 FF
    send_visca("8101060100000303FF")
    print("Done.")
