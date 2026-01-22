from PIL import Image
import numpy as np

def analyze(path):
    img = Image.open(path).convert("RGBA")
    data = np.array(img)
    # Get pixels with alpha > 0
    opaque_pixels = data[data[:, :, 3] > 0]
    if len(opaque_pixels) > 0:
        avg_color = np.mean(opaque_pixels[:, :3], axis=0)
        return avg_color, img.size
    return None, img.size

files = [
    "/Users/gimdongseong/Documents/GitHub/behringer-mixer/Design/Test/Text/system_initializing_text.png",
    "/Users/gimdongseong/Documents/GitHub/behringer-mixer/Design/Test/Text/press_start_text.png"
]

for f in files:
    color, size = analyze(f)
    print(f"{f}: Size={size}, AvgColor={color}")
