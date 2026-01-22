import socket
import time
import sys

TARGET_IP = "127.0.0.1"
TARGET_PORT = 1500

def run_test():
    print(f"--- 🔄 Auto-Tester: Connecting to Bridge at {TARGET_IP}:{TARGET_PORT} ---")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((TARGET_IP, TARGET_PORT))
        print("✅ Connected to Bridge!")
        
        # Test Loop
        states = ["1", "0"] # Mute ON / OFF
        idx = 0
        
        # Clear initial buffer
        sock.setblocking(False)
        try:
            while sock.recv(1024): pass
        except: pass
        sock.setblocking(True)
        sock.settimeout(3.0) # Wait up to 3s for feedback

        print("\n--- 🏁 Starting Loop (CH1 Mute Toggle) ---")
        print("Logic: Send Command -> Wait for Wing Feedback -> Print Result")
        
        for i in range(10): # Run 10 times (approx 30s)
            val = states[idx]
            cmd = f"SET ch1m {val}"
            print(f"\n[Test {i+1}] Sending: {cmd}")
            
            sock.sendall(cmd.encode())
            
            start_t = time.time()
            received = False
            while time.time() - start_t < 3.0:
                try:
                    data = sock.recv(1024)
                    if data:
                        decoded = data.decode().strip()
                        print(f"   🎉 RESPONSE: {decoded}")
                        received = True
                        if f"ch1m {val}" in decoded or f"ch1m true" in decoded.lower() or f"ch1m false" in decoded.lower():
                            print("   ✅ VERIFIED: Round-Trip Successful!")
                            break
                except socket.timeout:
                    break
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    break
            
            if not received:
                print("   ⚠️ NO RESPONSE (Feedback Loop Broken?)")
            
            idx = (idx + 1) % 2
            time.sleep(1.0)
            
    except ConnectionRefusedError:
        print("❌ Could not connect. Is the Bridge running?")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sock.close()
        print("\n--- 🛑 Test Finished ---")

if __name__ == "__main__":
    run_test()
