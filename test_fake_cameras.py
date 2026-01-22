from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query params (e.g., /cgi-bin/aw_ptz?cmd=%23PTS9950&res=1)
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        cmd = qs.get("cmd", [""])[0]
        
        # Identify Camera based on port
        port = self.server.server_port
        cam_name = "CAM1" if port == 8081 else "CAM2"
        
        # Decode Command (Simple mapping for demo)
        meaning = "Unknown"
        
        # Robust Checking (handling #, %23, or plain)
        if "PTS9950" in cmd: meaning = "➡️ RIGHT"
        elif "PTS0150" in cmd: meaning = "⬅️ LEFT"
        elif "PTS5099" in cmd: meaning = "⬆️ UP"
        elif "PTS5001" in cmd: meaning = "⬇️ DOWN"
        elif "PTS5050" in cmd: meaning = "🛑 STOP"
        elif "APC7FFF7FFF" in cmd: meaning = "🏠 HOME"
        elif "Z80" in cmd or "z80" in cmd: meaning = "🔍 ZOOM IN"
        elif "Z20" in cmd or "z20" in cmd: meaning = "🔭 ZOOM OUT"
        elif "Z50" in cmd or "z50" in cmd: meaning = "✋ ZOOM STOP"
        
        print(f"\n📸 [Mock {cam_name}] Received: {meaning} (cmd={repr(cmd)})")
        
        # Respond 200 OK
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        return # Suppress default logging

def run_server(port):
    try:
        server = HTTPServer(('0.0.0.0', port), CamHandler)
        print(f"✅ Mock Camera listening on port {port}...")
        server.serve_forever()
    except OSError as e:
        print(f"❌ Port {port} error: {e}")

# Run two servers
t1 = threading.Thread(target=run_server, args=(8081,), daemon=True)
t2 = threading.Thread(target=run_server, args=(8082,), daemon=True)
t1.start()
t2.start()

print("🎥 가상 카메라 서버 시작됨 (CAM1: 8081, CAM2: 8082)")
print("종료하려면 Ctrl+C")

try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    pass
