import socket
import time
import sys

TCP_IP = "127.0.0.1" # Bridge runs on localhost for test
TCP_PORT = 10001

def send_command(cmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(cmd.encode())
        s.close()
        print(f"Sent: {cmd.strip()}")
    except Exception as e:
        print(f"Error sending {cmd.strip()}: {e}")

if __name__ == "__main__":
    print("Simulating Xilica...")
    
    # Test Channel 1 Vol
    send_command("SET CH1_VOL -10.0\r\n")
    time.sleep(1)
    
    # Test Channel 2 Mute
    send_command("SET CH2_MUTE 1\r\n")
    time.sleep(1)
    
    # Test Main Vol
    send_command("SET MAIN_VOL -5.0\r\n")
    time.sleep(1)
    
    # Test Main Mute (should toggle Wing 'on' to 0)
    send_command("SET MAIN_MUTE 1\r\n") 
