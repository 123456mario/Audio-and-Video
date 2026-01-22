from PIL import Image
import os
import numpy as np

def get_green_pixels_mask(img_np):
    # img_np is (H, W, 4)
    r, g, b, a = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2], img_np[:, :, 3]
    # Green dominant: G > R and G > B and Alpha is high
    mask = (g.astype(int) > r.astype(int)) & (g.astype(int) > b.astype(int)) & (a > 50)
    return mask

def get_avg_green_color(img_path):
    img = Image.open(img_path).convert("RGBA")
    img_np = np.array(img)
    w = img_np.shape[1]
    
    # Only look at the right half ('y' part)
    right_half = img_np[:, w // 2:, :]
    mask = get_green_pixels_mask(right_half)
    
    if not np.any(mask):
        return None
    
    avg_color = right_half[mask].mean(axis=0)
    return avg_color[:3] # Return RGB

def apply_color_fix(target_path, ref_color):
    img = Image.open(target_path).convert("RGBA")
    img_np = np.array(img, dtype=np.float32)
    w = img_np.shape[1]
    
    right_half = img_np[:, w // 2:, :]
    mask = get_green_pixels_mask(right_half.astype(np.uint8))
    
    if not np.any(mask):
        print(f"No green pixels found in {target_path}")
        return
    
    current_avg = right_half[mask].mean(axis=0)[:3]
    delta = ref_color - current_avg
    
    print(f"Fixing {os.path.basename(target_path)}: Current {current_avg.astype(int)}, Ref {ref_color.astype(int)}, Delta {delta.astype(int)}")
    
    # Apply delta to all pixels in the right half that are "green-ish"
    # To avoid artifacts at edges, we can apply it to the mask region
    # But often it's better to apply to any pixel that contributes to the 'y' shape.
    # We'll apply it to the mask region.
    
    for i in range(3): # R, G, B
        right_half[mask, i] += delta[i]
    
    # Clip and convert back to uint8
    img_np[:, w // 2:, :] = np.clip(right_half, 0, 255)
    final_img = Image.fromarray(img_np.astype(np.uint8))
    final_img.save(target_path)

if __name__ == "__main__":
    base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text/ky_찬다"
    ref_img_path = os.path.join(base_dir, "10.png")
    
    ref_color = get_avg_green_color(ref_img_path)
    if ref_color is None:
        print("Error: Could not find reference color in 10.png")
        exit(1)
    
    print(f"Reference Color (10.png): {ref_color.astype(int)}")
    
    for i in range(1, 10):
        target_path = os.path.join(base_dir, f"{i}.png")
        if os.path.exists(target_path):
            apply_color_fix(target_path, ref_color)
        else:
            print(f"Skipping {target_path} - file not found")
