from PIL import Image
import os
import numpy as np

def get_avg_green_color(img_path):
    img = Image.open(img_path).convert("RGBA")
    img_np = np.array(img)
    w = img_np.shape[1]
    r, g, b, a = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2], img_np[:, :, 3]
    right_half_mask = (g.astype(int) > r.astype(int)) & (g.astype(int) > b.astype(int)) & (a > 50)
    # Correct mask for right half index
    mask = right_half_mask[:, w // 2:]
    right_half_pixels = img_np[:, w // 2:, :]
    
    if not np.any(mask):
        return None
    
    return right_half_pixels[mask].mean(axis=0)[:3]

base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text/ky_찬다"

print("Final Color Verification:")
ref_color = get_avg_green_color(os.path.join(base_dir, "10.png"))
print(f"Reference (10.png): {ref_color.astype(int)}")

for i in range(1, 10):
    path = os.path.join(base_dir, f"{i}.png")
    if os.path.exists(path):
        avg = get_avg_green_color(path)
        print(f"Image {i}.png: {avg.astype(int)} (Diff: {(avg - ref_color).astype(int)})")
