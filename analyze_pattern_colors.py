from PIL import Image
import os
from collections import Counter

def list_top_colors(img_path):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    pixels = []
    for x in range(w // 2, w):
        for y in range(h // 2, h):
            pixel = img.getpixel((x, y))
            if pixel[3] > 100:
                r, g, b, a = pixel
                if g > r and g > b:
                    pixels.append((r, g, b))
    
    counts = Counter(pixels)
    return counts.most_common(10)

base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text/ky_찬다"
print("Top colors in 10.png right half:")
for c, count in list_top_colors(os.path.join(base_dir, "10.png")):
    print(f"{c}: {count}")

print("\nTop colors in 1.png right half:")
for c, count in list_top_colors(os.path.join(base_dir, "1.png")):
    print(f"{c}: {count}")
