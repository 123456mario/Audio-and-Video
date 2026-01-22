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
                low_data = data.lower()
                if b"password:" in low_data:
                    os.write(fd, f"{PASS}\n".encode())
            except OSError:
                break
        os.waitpid(pid, 0)
        return output.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("--- 30번 vs 31번 카메라 네트워크 비교 (Ping) ---")
    print("\n[CAM1 - 192.168.1.30]")
    print(run_ssh_cmd(f"ssh {USER}@{HOST} 'ping -c 5 192.168.1.30'"))
    
    print("\n[CAM2 - 192.168.1.31]")
    print(run_ssh_cmd(f"ssh {USER}@{HOST} 'ping -c 5 192.168.1.31'"))
    
    print("\n--- 최근 31번 카메라(CAM2) 조작 로그 확인 ---")
    # CAM2가 포함된 로그만 필터링해서 확인
    print(run_ssh_cmd(f"ssh {USER}@{HOST} 'grep 192.168.1.31 ~/behringer-mixer/ptz_log.txt | tail -n 20'"))
