from PIL import Image
import os
import numpy as np

def check_flatness(img_path):
    img = Image.open(img_path).convert("RGBA")
    img_np = np.array(img)
    w = img_np.shape[1]
    
    right_half = img_np[:, w // 2:, :]
    r, g, b, a = right_half[:,:,0], right_half[:,:,1], right_half[:,:,2], right_half[:,:,3]
    
    # Same mask as detection
    mask = (g.astype(int) > r.astype(int) + 10) & (g.astype(int) > b.astype(int) + 10) & (a > 100)
    
    if not np.any(mask):
        return True, 0
    
    # Get all colors in the masked area
    green_pixels = right_half[mask, :3]
    unique_colors = np.unique(green_pixels, axis=0)
    
    return len(unique_colors) == 1, len(unique_colors)

if __name__ == "__main__":
    base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text/ky_찬다"
    for i in range(1, 11):
        path = os.path.join(base_dir, f"{i}.png")
        if os.path.exists(path):
            flat, count = check_flatness(path)
            status = "Flat" if flat else f"NOT FLAT ({count} colors)"
            print(f"{os.path.basename(path)}: {status}")
