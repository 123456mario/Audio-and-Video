from PIL import Image
import os

DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/button"
files = ["top_active.png", "top_dim.png", "bottom_active.png", "bottom_dim.png"]

print(f"{'File':<20} | {'Center Pixel (RGBA)':<20} | {'Hex'}")
print("-" * 60)

for f in files:
    path = os.path.join(DIR, f)
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        width, height = img.size
        # Sample center
        center_px = img.getpixel((width//2, height//2))
        
        # Hex (ignoring alpha for hex string usually, but let's show RGB)
        hex_col = "#{:02x}{:02x}{:02x}".format(center_px[0], center_px[1], center_px[2])
        
        print(f"{f:<20} | {str(center_px):<20} | {hex_col}")
    else:
        print(f"{f:<20} | NOT FOUND")
