from pythonosc import osc_message_builder
import struct

address = "/ch/1/fdr"
value = -10.0

print(f"--- Debugging OSC Packet for {address} {value} ---")

# Method 1: Manual Builder (Legacy Style)
msg1 = osc_message_builder.OscMessageBuilder(address=address)
msg1.add_arg(float(value)) # Default float
dgram1 = msg1.build().dgram
print(f"Legacy Builder Hex: {dgram1.hex()}")

# Analyze Payload
# Address + Padding + TypeTag + Padding + Value
print(f"Length: {len(dgram1)}")

# Method 2: Explicit Float (just to be sure)
msg2 = osc_message_builder.OscMessageBuilder(address=address)
msg2.add_arg(value, arg_type='f') 
dgram2 = msg2.build().dgram
print(f"Explicit Float Hex: {dgram2.hex()}")

if dgram1 == dgram2:
    print("Optimization: Simple float adds as 'f' (32-bit). Correct.")
else:
    print("WARNING: Default add_arg differs from explicit 'f'.")

# Decode value bytes
val_bytes = dgram1[-4:]
unpacked = struct.unpack('>f', val_bytes)[0]
print(f"Encoded Value: {unpacked}")
