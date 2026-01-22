
def calc_checksum(hex_str):
    parts = bytes.fromhex(hex_str.replace(" ", ""))
    # Payload is all except last 2 bytes
    payload = parts[:-2]
    expected = parts[-2:]
    
    total = sum(payload)
    print(f"Hex: {hex_str}")
    print(f"Sum (Dec): {total}")
    print(f"Sum (Hex): {total:04x}")
    print(f"Sum (Little Endian): {(total & 0xFF):02x} {(total >> 8):02x}")
    print(f"Expected: {expected.hex()}\n")
    
    # Try alternate: Sum + 0x5555
    total_plus = total + 0x5555
    print(f"Sum + 0x5555 (Hex): {total_plus:04x}")
    print(f"Sum + 0x5555 (LE): {(total_plus & 0xFF):02x} {(total_plus >> 8):02x}")


# Known Brightness Command
calc_checksum("55 aa 00 00 fe 00 00 00 00 00 00 00 04 00 00 00 01 00 ff ca 56")

# Proposed Ping Command
calc_checksum("55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56")
