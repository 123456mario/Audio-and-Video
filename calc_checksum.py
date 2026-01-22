# Pro Series Checksum Logic: Sum + 0x5555

def calc_pro_cmd(payload_bytes):
    checksum = sum(payload_bytes) + 0x5555
    sum_l = checksum & 0xFF
    sum_h = (checksum >> 8) & 0xFF
    full_cmd = b'\x55\xaa' + payload_bytes + bytes([sum_l, sum_h])
    return full_cmd.hex()

print("--- Brightness Commands (Pro Series) ---")
# Header for Brightness: 00 00 fe ff 01 ff ff ff 01 00 01 00 00 02 01 00
bri_header = bytes.fromhex("00 00 fe ff 01 ff ff ff 01 00 01 00 00 02 01 00")

brightness_levels = {
    "20%": 51,  # 0x33
    "40%": 102, # 0x66
    "60%": 153, # 0x99
    "80%": 204, # 0xCC
    "100%": 255 # 0xFF
}

for label, val in brightness_levels.items():
    payload = bri_header + bytes([val])
    print(f"Brightness {label} ({hex(val)}): {calc_pro_cmd(payload)}")

print("\n--- Preset Load Commands (Pro Series) ---")
# Header for Preset: 00 00 fe 00 00 00 00 00 01 00 00 01 51 13 01 00
# Note: The search result showed "55 AA ... 01 51 13 01 00 XX SUM".
# Let's verify the header length. 
# Brightness header length after 55aa was 16 bytes + 1 byte data = 17 bytes payload.
# Preset header length seems similar.
# The search result `55 AA 00 00 FE 00 00 00 00 00 01 00 00 01 51 13 01 00 XX`
# Payload is `00 00 FE 00 00 00 00 00 01 00 00 01 51 13 01 00` (16 bytes) + XX (1 byte) = 17 bytes.
# This matches the structure consistency.
preset_header = bytes.fromhex("00 00 fe 00 00 00 00 00 01 00 00 01 51 13 01 00")

for i in range(1, 4): # Presets 1, 2, 3
    # Search said Preset 1 is 00, Preset 2 is 01
    preset_val = i - 1 
    payload = preset_header + bytes([preset_val])
    print(f"Preset {i}: {calc_pro_cmd(payload)}")
