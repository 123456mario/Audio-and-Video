from pythonosc import dispatcher
from pythonosc import osc_server
import socket

XILICA_IP = "192.168.1.20"   # Xilica Solaro IP

def send_to_xilica(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((XILICA_IP, 10007))  # 공식 API 포트 10007
            s.sendall((command + "\r").encode())
            resp = s.recv(1024).decode()
            print(f"Xilica API Response: {resp.strip()}")
    except Exception as e:
        print(f"Xilica API Error: {e}")

def wing_feedback_handler(address, *args):
    print(f"Wing → Xilica Feedback: {address} {args}")
    
    if "mute" in address:
        value = 1 if args[0] > 0.5 else 0
        send_to_xilica(f"SET CH1_Mute {value}")
    elif "fdr" in address:
        db = args[0]
        # dB → Numeric 레벨 변환 (0~5)
        levels = [-80, -40, -10, 0, 5, 18]
        level = 3
        for i, v in enumerate(levels):
            if abs(v - db) < abs(levels[level] - db):
                level = i
        send_to_xilica(f"SET CH1_Volume {level}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/ch/01/mute", wing_feedback_handler)
dispatcher.map("/ch/01/fdr", wing_feedback_handler)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 50000), dispatcher)
print("Wing Feedback → Xilica API 서버 실행 중 (UDP 50000)")
server.serve_forever()