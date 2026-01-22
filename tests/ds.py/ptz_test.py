import socket
import requests
from requests.auth import HTTPDigestAuth
import threading
import time

# PTZ Camera IPs and Credentials
CAM1_IP = "192.168.1.30"
CAM2_IP = "192.168.1.31"
USERNAME = "admin"
PASSWORD = "1234"  # If not working, try "12345"



def control_ptz(cam_ip, command):
    url = f"http://{cam_ip}/cgi-bin/aw_ptz?cmd={command}&res=1"
    print(f"Sending URL: {url}")  # 디버깅 구문
    response = requests.get(url, auth=HTTPDigestAuth(USERNAME, PASSWORD))
    print(f"[Response] Status Code: {response.status_code}")  # 요청 결과 로그
    if response.status_code == 200:
        print(f"Sent to {cam_ip}: {command} - Response: {response.text}")
    else:
        print(f"Error sending to {cam_ip}: {response.status_code} - {response.text}")