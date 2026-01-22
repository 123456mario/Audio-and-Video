import pty
import os

HOST = "192.168.1.50"
USER = "pi"
PASS = "4200"

def run_ssh_cmd(cmd):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        output = b""
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                output += data
                if b"password:" in data.lower():
                    os.write(fd, f"{PASS}\n".encode())
            except OSError:
                break
        os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- 30번 vs 31번 상세 비교 데이터 ---")
    
    # Check if Pi can see Camera 31 at all
    print("\n1. 31번 카메라 네트워크 확인:")
    print(run_ssh_cmd(f"ssh {USER}@{HOST} 'ping -c 3 -W 1 192.168.1.31'"))
    
    print("\n2. 최근 조작 로그 (마지막 100줄):")
    # Fetch more logs to catch CAM2 activity
    logs = run_ssh_cmd(f"ssh {USER}@{HOST} 'tail -n 100 ~/behringer-mixer/ptz_log.txt'")
    print(logs)
    
    # Calculate average response times from the logged data
    import re
    def calc_avg(ip, text):
        times = re.findall(rf"{ip} \|.*?Net: ([\d.]+)ms", text)
        if not times: return "데이터 없음"
        times = [float(t) for t in times]
        return f"{sum(times)/len(times):.1f}ms (샘플: {len(times)}개)"

    print("\n3. 성능 통계 분석:")
    print(f"30번(CAM1) 평균 응답력: {calc_avg('192.168.1.30', logs)}")
    print(f"31번(CAM2) 평균 응답력: {calc_avg('192.168.1.31', logs)}")
