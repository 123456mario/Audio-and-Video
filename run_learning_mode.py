import logging
from xilica_driver import XilicaDriver
import time
import sys

# Configure Logging to show everything clearly
logging.getLogger("XilicaDriver").setLevel(logging.INFO)

def main():
    print("="*60)
    print(" 🎓 Xilica Smart Protocol Learner")
    print("="*60)
    print("This tool will help you teach the driver how your specific")
    print("Xilica device communicates, by listening to real traffic.")
    print("-" * 60)

    # 1. Setup
    default_ip = "192.168.1.50" # Based on history
    ip = input(f"Enter Xilica IP [{default_ip}]: ").strip() or default_ip
    
    print(f"\nTarget set to {ip}. Which protocol to sniff?")
    print("1. TCP (Most Xilica panels use this)")
    print("2. UDP (Some older configurations)")
    proto_choice = input("Select [1/2] (Default 1): ").strip()
    protocol = 'UDP' if proto_choice == '2' else 'TCP'

    driver = XilicaDriver(ip, port=10025, protocol=protocol)
    
    # Load existing if any
    driver.load_protocol()
    
    if not driver.connect():
        print("❌ Could not connect to device. Check network/cable.")
        sys.exit(1)
        
    print(f"\n✅ Connected via {protocol}!")
    
    while True:
        print("\n" + "="*40)
        print(" ACTION MENU")
        print("="*40)
        print("1. 👂 TEACH NEW COMMAND (Listen to device)")
        print("2. ▶️  TEST COMMAND (Replay learned)")
        print("3. 💾 SAVE CONFIGURATION")
        print("4. ❌ EXIT")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            name = input("Enter Logical Name (e.g., MUTE_ON_CH1): ").strip().upper()
            if not name: continue
            
            print(f"\n>>> Please PRESS the physical button for '{name}' on the Xilica panel NOW...")
            print(">>> Listening for 10 seconds...")
            
            data = driver.listen_raw(timeout=10)
            
            if data:
                print(f"\n🎯 CAPTURED DATA: {data}")
                # Heuristic: Is it Hex or String?
                try:
                    decoded = data.decode('utf-8')
                    # Simple check: if it looks like garbage, treat as hex
                    if sum(1 for c in decoded if not c.isprintable()) > 2:
                        raise ValueError("Likely binary")
                    
                    print(f"   (Identified as Text string: '{decoded.strip()}')")
                    driver.protocol_map[name] = {'cmd': decoded, 'type': 'string'}
                except:
                    hex_str = data.hex()
                    print(f"   (Identified as Binary Hex: {hex_str})")
                    driver.protocol_map[name] = {'cmd': hex_str, 'type': 'hex'}
                    
                print("✅ Command learned!")
            else:
                print("\n❌ Timeout. No data received. Did you create the button link?")
                
        elif choice == '2':
            if not driver.protocol_map:
                print("No commands learned yet!")
                continue
                
            print("\nAvailable Commands:")
            for cmd in driver.protocol_map:
                print(f"- {cmd}")
            
            target = input("Type command to test: ").strip().upper()
            if target in driver.protocol_map:
                print(f"Sending {target}...")
                driver.send_command(target)
            else:
                print("Invalid name.")
                
        elif choice == '3':
            driver.save_protocol()
            print("💾 Saved to config_learned.json")
            
        elif choice == '4':
            print("Bye!")
            break

if __name__ == "__main__":
    main()
