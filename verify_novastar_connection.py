import socket
import sys
import time

TARGET_IP = "192.168.1.60"
PORT = 5200

# Function to calculate checksum (Sum + 0x5555)
def get_novastar_cmd(base_hex):
    # Remove spaces and get bytes
    b = bytes.fromhex(base_hex.replace(" ", ""))
    # Payload is everything
    # Checksum is 2 bytes at end
    # Standard Novastar: Sum of all bytes (including header?) + 0x5555
    # Let's try to append checksum
    
    # Calculate sum of base
    total = sum(b) + 0x5555
    checksum_bytes = total.to_bytes(2, byteorder='little') # Try Little Endian first?
    # Wait, user example 57 56 -> 0x5657? Or 0x5756?
    # My manual calc 57 54 matched 0x5754 (Big Endian of result)
    # Let's try Big Endian for checksum
    checksum_bytes_be = total.to_bytes(2, byteorder='big')
    
    return b + checksum_bytes_be

# Variant 1: User's Exact Hex (Checksum 57 56)
CMD_USER = bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56".replace(" ", ""))

# Variant 2: Calculated Checksum (0x5555 + Sum) -> Should be 57 54
CMD_CALC_BASE = "55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00"
CMD_AUTO = get_novastar_cmd(CMD_CALC_BASE) 
# Note: get_novastar_cmd adds checksum. 
# 0x1FF + 0x5555 = 0x5754. Big Endian -> 57 54.

COMMANDS = [
    ("User Provided (57 56)", CMD_USER),
    ("Calculated (57 54)", bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 54")),
     # Try Little Endian 54 57 just in case
    ("Calculated LE (54 57)", bytes.fromhex("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 54 57")),
]

def test_udp(cmd_name, cmd_bytes):
    print(f"🔵 UDP: Sending {cmd_name}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.sendto(cmd_bytes, (TARGET_IP, PORT))
        
        data, addr = s.recvfrom(1024)
        print(f"   ✅ RESPONSE: {data.hex()}")
        return True
    except socket.timeout:
        print("   ❌ Timeout")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        s.close()
    return False

def test_tcp(cmd_name, cmd_bytes):
    print(f"🟠 TCP: Sending {cmd_name}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect((TARGET_IP, PORT))
        s.send(cmd_bytes)
        
        data = s.recv(1024)
        print(f"   ✅ RESPONSE: {data.hex()}")
        s.close()
        return True
    except socket.timeout:
        print("   ❌ Timeout")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return False

if __name__ == "__main__":
    print(f"🔍 Probing Novastar at {TARGET_IP}:{PORT}")
    
    for name, cmd in COMMANDS:
        if test_tcp(name, cmd):
            print(f"\n🎉 SUCCESS with {name} via TCP!")
            sys.exit(0)
        if test_udp(name, cmd):
            print(f"\n🎉 SUCCESS with {name} via UDP!")
            sys.exit(0)
        time.sleep(0.5)

    print("\n💀 All attempts failed.")
