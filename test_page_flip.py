import socket
import time

TCP_IP = "127.0.0.1"
TCP_PORT = 10001

def send_page_command(page_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        cmd = f"PAGE {page_name}\r\n"
        s.send(cmd.encode())
        print(f"Sent: {cmd.strip()}")
        
        # Read response
        data = s.recv(1024)
        print(f"Received: {data.decode().strip()}")
        s.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Test 1: Trigger Main View Page Flip")
    send_page_command("MAIN_VIEW")
    
    print("\nTest 2: Trigger Camera Control Page Flip")
    send_page_command("CAM_CTRL")
