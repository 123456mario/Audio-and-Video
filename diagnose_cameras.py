import requests
from requests.auth import HTTPDigestAuth
import time

CAM1_IP = "192.168.1.30"
CAM2_IP = "192.168.1.31"
USERNAME = "admin"
PASSWORD = "1234"

def test_camera(cam_ip, cam_name):
    print(f"\n--- Testing {cam_name} ({cam_ip}) ---")
    # Using STOP command as a safe connectivity test
    url = f"http://{cam_ip}/cgi-bin/aw_ptz?cmd=%23PTS5050&res=1"
    try:
        print(f"Sending STOP command to {cam_name}...")
        response = requests.get(url, auth=HTTPDigestAuth(USERNAME, PASSWORD), timeout=5)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        if response.status_code == 200:
            print(f"✅ {cam_name} is responding correctly.")
            return True
        else:
            print(f"❌ {cam_name} returned error status.")
            return False
    except Exception as e:
        print(f"❌ {cam_name} connection failed: {e}")
        return False

if __name__ == "__main__":
    c1_ok = test_camera(CAM1_IP, "CAM1")
    c2_ok = test_camera(CAM2_IP, "CAM2")
    
    print("\n--- Final Result ---")
    print(f"CAM1: {'SUCCESS' if c1_ok else 'FAILED'}")
    print(f"CAM2: {'SUCCESS' if c2_ok else 'FAILED'}")
