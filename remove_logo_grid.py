from PIL import Image, ImageFilter
import os
import numpy as np

def remove_grid(img_path, target_color):
    """
    Identifies the green fill in the right half and flattens its color.
    """
    img = Image.open(img_path).convert("RGBA")
    img_np = np.array(img)
    h, w, _ = img_np.shape
    
    # Process only the right half
    right_half = img_np[:, w // 2:, :]
    r, g, b, a = right_half[:,:,0], right_half[:,:,1], right_half[:,:,2], right_half[:,:,3]
    
    # Identify green pixels (G > R and G > B and significant alpha)
    # We use a threshold to capture all variations of the green grid
    mask = (g.astype(int) > r.astype(int) + 10) & (g.astype(int) > b.astype(int) + 10) & (a > 100)
    
    if not np.any(mask):
        print(f"Skipping {os.path.basename(img_path)}: No significant green area found.")
        return

    # Replace colors in the masked area with target_color
    new_right_half = right_half.copy()
    for i in range(3): # R, G, B
        new_right_half[mask, i] = target_color[i]
    
    # Re-assemble
    img_np[:, w // 2:, :] = new_right_half
    
    # Optional: Smooth the edges of the mask to avoid "aliasing"
    # We can do this by converting back to PIL and applying a very small blur 
    # but only on the right half or using a more sophisticated approach.
    # For now, simple replacement is usually enough for these UI assets.
    
    final_img = Image.fromarray(img_np)
    final_img.save(img_path)
    print(f"✅ Flattened color in {os.path.basename(img_path)}")

if __name__ == "__main__":
    base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text/ky_찬다"
    target_green = (141, 196, 61) # Reference from 10.png
    
    for i in range(1, 11):
        path = os.path.join(base_dir, f"{i}.png")
        if os.path.exists(path):
            remove_grid(path, target_green)
        else:
            print(f"File not found: {path}")
