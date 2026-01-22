import socket
import time

IP = "192.168.1.9" # Bridge is listening here
PORT = 10001
CMD_TRUE = "set ch1m true\r\n"
CMD_FALSE = "set ch1m false\r\n"

def send(cmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        print(f"Sending: {cmd.strip()}")
        s.send(cmd.encode())
        resp = s.recv(1024)
        print(f"Response: {resp.decode().strip()}")
        s.close()
    except Exception as e:
        print(f"Error: {e}")

print("Testing Boolean 'true'...")
send(CMD_TRUE)
time.sleep(2)
print("Testing Boolean 'false'...")
send(CMD_FALSE)
