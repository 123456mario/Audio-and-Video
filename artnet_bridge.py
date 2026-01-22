import socket
import struct
import time
import logging

# --- CONFIGURATION ---
XILICA_BIND_PORT = 10021       # Port to listen for Xilica Binary Commands
DMX_NODE_IP = "192.168.1.100"  # Target Art-Net Node
DMX_NODE_PORT = 6454           # Standard Art-Net Port

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("artnet_bridge")

# Art-Net Header Constant
# ID (8) + OpCode (2) + ProtoVer (2)
ARTNET_HEADER = b'Art-Net\x00' + struct.pack('<H', 0x5000) + struct.pack('>H', 14)

def create_artdmx_packet(universe, data_channels):
    """
    Constructs an ArtDmx packet.
    universe: int (0-15 typically for local net)
    data_channels: list or bytes of DMX values (512 bytes max)
    """
    # Sequence (1) + Physical (1) + Universe (2) + Length (2)
    # Sequence = 0 (disable)
    # Physical = 0
    # Universe = Little Endian
    # Length = Big Endian
    
    length = len(data_channels)
    if length > 512:
        length = 512
        data_channels = data_channels[:512]
        
    packet = ARTNET_HEADER
    packet += struct.pack('B', 0) # Sequence
    packet += struct.pack('B', 0) # Physical
    packet += struct.pack('<H', universe) # Universe
    packet += struct.pack('>H', length) # Length
    
    if isinstance(data_channels, bytes):
        packet += data_channels
    else:
        packet += bytes(data_channels)
        
    return packet

def main():
    logger.info(f"Starting Art-Net Bridge on port {XILICA_BIND_PORT}")
    logger.info(f"Target DMX Node: {DMX_NODE_IP}:{DMX_NODE_PORT}")

    # UDP Server for Xilica
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', XILICA_BIND_PORT))

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            
            # Protocol supports both Binary and Text for debugging
            # Text Format: "UNIV:0 VAL:255"
            # Binary Format: [Universe Byte] [Value Byte] (Legacy)

            try:
                decoded_str = data.decode('utf-8').strip()
                if decoded_str.startswith("UNIV:"):
                    # Parse Text Command
                    # Expected: UNIV:0 VAL:255
                    parts = decoded_str.split()
                    univ_part = parts[0].split(':')[1]
                    val_part = parts[1].split(':')[1]
                    
                    univ = int(univ_part)
                    val = int(val_part)
                    
                    logger.info(f"Received TEXT from {addr}: Universe={univ}, Value={val}")
                    process_dmx(univ, val)
                    continue
            except Exception:
                pass # Not a text command, try binary
            
            if len(data) >= 2:
                # Parse Binary
                univ = data[0]
                val = data[1]
                
                logger.info(f"Received BINARY from {addr}: Universe={univ}, Value={val}")
                process_dmx(univ, val)
                    
            else:
                logger.warning(f"Ignored malformed data from {addr}: {data.hex()}")

    except KeyboardInterrupt:
        logger.info("Stopping Bridge...")
# Global DMX State - Multi-Universe Support
# Keys: Physical Output Universe ID (0=Port A, 1=Port B, etc.)
dmx_states = {
    0: [0] * 512,
    1: [0] * 512,
    2: [0] * 512,
    3: [0] * 512
}

def process_dmx(univ, val):
    global dmx_states


    targets = []
    
    # --- MAPPING CONFIGURATION ---
    # Input 1 (Univ 0) -> DMX 7, 8 (Group A)
    # Input 2 (Univ 1) -> DMX 9, 10 (Group B)
    # Input 3 (Univ 2) -> DMX 7, 8 (Group A - Duplicate control)
    
    # Ensure univ is int
    try:
        univ = int(univ)
    except ValueError:
        logger.error(f"Invalid universe value: {univ}")
        return

    # GROUP A: DMX 7 & 8 -> Physical Universe 0 (Port A)
    # Map from Universe 0 (Input 1) OR Universe 2 (Input 3) OR Universe 6
    if univ in [0, 2, 6]: 
        targets = [7, 8]
        output_universe = 0
        logger.info(f"[MAPPING] Input Univ {univ} -> Output Univ {output_universe} (Port A) [DMX 7,8] | VAL: {val}")
        
    # GROUP B: DMX 9 & 10 -> Physical Universe 1 (Port B)
    # Map from Universe 1 (Input 2) OR Universe 3 OR Universe 8
    elif univ in [1, 3, 8]: 
        targets = [9, 10]
        output_universe = 1
        logger.info(f"[MAPPING] Input Univ {univ} -> Output Univ {output_universe} (Port B) [DMX 9,10] | VAL: {val}")
        
    # Legacy / specific handling
    elif univ == 4: 
        targets = [5]
        output_universe = 0 # Default to A
        logger.info(f"[MAPPING] Input Univ {univ} -> Output Univ {output_universe} (Port A) [DMX 5] | VAL: {val}")
    
    else:
        logger.warning(f"[UNMATCHED] Input Univ {univ} received but has no mapping rule! VAL: {val}")
        return
    
    if targets:
        # Select the correct state array for the target physical universe
        current_state = dmx_states[output_universe]
        
        for t in targets:
            idx = t - 1 # 0-based index
            if 0 <= idx < 512:
                current_state[idx] = val
        
        # Send to the SPECIFIC Physical Universe
        packet = create_artdmx_packet(output_universe, current_state)
        
        # LOGGING STATE for Debugging
        # Only show relevant channels for that universe
        if output_universe == 0:
            state_slice = current_state[6:8] # Ch 7, 8
            logger.info(f"[OUT] Sending Univ 0. Ch 7-8: {state_slice}")
        elif output_universe == 1:
            state_slice = current_state[8:10] # Ch 9, 10
            logger.info(f"[OUT] Sending Univ 1. Ch 9-10: {state_slice}")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.sendto(packet, (DMX_NODE_IP, DMX_NODE_PORT))
    else:
        logger.debug(f"Univ {univ} has no mapping.")


if __name__ == "__main__":
    main()
