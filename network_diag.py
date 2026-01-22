import os
import sys
import socket
import time

TARGET_IP = "192.168.1.11"
TARGET_PORT = 2223
LISTEN_PORT = 2223 # Same port for bidirectional

def run_command(cmd):
    print(f"Executing: {cmd}")
    os.system(cmd)
    print("-" * 20)

def osc_ping():
    print(f"\n--- 📡 OSC Ping Test (/? -> {TARGET_IP}:{TARGET_PORT}) ---")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    
    try:
        # Bind to listening port
        # Note: This might fail if the bridge is running. 
        # We will try to bind, if fail we assume bridge is running and just send.
        try:
            sock.bind(("0.0.0.0", LISTEN_PORT))
            print(f"Bound to port {LISTEN_PORT} successfully (Bridge is likely OFF)")
        except:
            print(f"⚠️ Could not bind to {LISTEN_PORT} (Bridge is likely ON). sending as anonymous client.")
            # If we don't bind to 2223, we bind to random. 
            # Wing might reply to random port for /? query.
            pass
            
        print("Sending '/?' ...")
        sock.sendto(b"/?\0", (TARGET_IP, TARGET_PORT))
        
        try:
            data, addr = sock.recvfrom(1024)
            print(f"✅ RECEIVED RESPONSE from {addr}: {data}")
            print(">>> OSC CONNECTIVITY IS WORKING! <<<")
        except socket.timeout:
            print("❌ TIMEOUT: No response received to OSC Ping.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    print("=== 🛠️ Raspberry Pi Network Diagnostics ===")
    
    # 1. PING
    print("\n[1] PING TEST")
    run_command(f"ping -c 4 {TARGET_IP}")
    
    # 2. ARP
    print("\n[2] ARP TABLE (Check local MAC resolution)")
    run_command("arp -a")
    
    # 3. OSC PING
    # Use pkill to stop bridge temporarily to free the port for strict testing
    print("\n[3] STOPPING BRIDGE FOR PRECISE PORT TEST...")
    run_command("pkill -f osc_bridge_final.py")
    time.sleep(1)
    
    osc_ping()
    
    print("\n=== DIAGNOSTIC COMPLETE ===")
