
import socket
import sys

def sniff():
    print("🚀 Python Raw Sniffer Started... Listening for 'SET' or 'CH'...")
    try:
        # AF_PACKET is Linux specific, captures all Ethernet frames
        # 0x0003 is ETH_P_ALL (capture all protocols)
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    except AttributeError:
        print("❌ Error: AF_PACKET not supported (Are you on Linux/Pi?)")
        sys.exit(1)
    except PermissionError:
        print("❌ Error: Permission denied. Run with sudo!")
        sys.exit(1)

    while True:
        try:
            raw_data, addr = s.recvfrom(65535)
            # Try to decode as much as possible
            try:
                # Replace errors to avoid crash on binary data
                text = raw_data.decode('utf-8', errors='ignore') 
                
                # Check for Xilica keywords
                if "SET" in text.upper() or "CH" in text.upper() or "MUTE" in text.upper():
                    print(f"🔎 CAPTURED: {repr(text)}")
                    
            except Exception as e:
                pass
                
        except KeyboardInterrupt:
            print("\nUpdating...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    sniff()
