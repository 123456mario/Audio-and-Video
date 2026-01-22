import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
original_ref_path = os.path.join(brain_dir, "uploaded_image_1767930732903.png")
cleaned_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_perfect_match_buttons():
    try:
        # --- 1. Mute Button: Smart Crop Red Region ---
        img = Image.open(original_ref_path).convert("RGBA")
        # Convert to numpy array for color detection
        arr = np.array(img)
        
        # Detect Red Pixels
        # R > 100, G < 100, B < 100 (Adjust thresholds as needed)
        r = arr[:,:,0]
        g = arr[:,:,1]
        b = arr[:,:,2]
        
        # Mask where pixels are "Reddish"
        mask = (r > 150) & (g < 80) & (b < 80)
        
        # Find bounds of this mask
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            print("Could not find red region. Using full image.")
            crop_box = (0, 0, img.width, img.height)
        else:
            ymin, ymax = np.where(rows)[0][[0, -1]]
            xmin, xmax = np.where(cols)[0][[0, -1]]
            
            # ymax and xmax are indices, so add 1 for slice/crop
            crop_box = (xmin, ymin, xmax+1, ymax+1)
            print(f"Cropping to Red Region: {crop_box}")

        img_cropped = img.crop(crop_box)
        
        # Resize to 90x70 (Exact User Request)
        mute_btn = img_cropped.resize((90, 70), Image.Resampling.LANCZOS)
        
        mute_path = os.path.join(output_dir, "btn_mute_active.png")
        mute_btn.save(mute_path)
        print(f"Saved matched Mute: {mute_path}")

        # --- 2. Unmute Button: Match Size & Style ---
        # Create a background that matches the Mute button's background shape/size.
        # Since Mute is a resized bitmap, it fills 90x70.
        # We will create a Vector background of 90x70.
        
        unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw = ImageDraw.Draw(unmute_btn)
        
        # To match the "Corner Radius" of the resized bitmap:
        # The original looked like a standard app icon.
        # Let's guess radius 14px (20% of height).
        bg_color = (235, 235, 235, 255)
        draw.rounded_rectangle((0, 0, 90, 70), radius=14, fill=bg_color)
        
        # --- Overlay Cleaned Icon ---
        img_clean = Image.open(cleaned_icon_path).convert("RGBA")
        
        # Extract Icon (Black) from White BG
        gray = img_clean.convert("L")
        icon_alpha = ImageOps.invert(gray) # White BG(255)->0 alpha, Black Icon(0)->255 alpha
        
        bbox_icon = icon_alpha.getbbox()
        if bbox_icon:
            icon_crop = img_clean.crop(bbox_icon)
            alpha_crop = icon_alpha.crop(bbox_icon)
        else:
            icon_crop = img_clean
            alpha_crop = icon_alpha
            
        # Resize Icon
        # Maintain aspect ratio, fit within ~60% height
        target_h = int(70 * 0.6)
        w, h = icon_crop.size
        ratio = w / h
        target_w = int(target_h * ratio)
        
        # Colorize Icon to Dark Grey
        icon_layer = Image.new("RGBA", (target_w, target_h), (50, 50, 50, 255))
        # Resize alpha mask
        alpha_resized = alpha_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
        icon_layer.putalpha(alpha_resized)
        
        # Composite
        pos_x = (90 - target_w) // 2
        pos_y = (70 - target_h) // 2
        
        unmute_btn.alpha_composite(icon_layer, (pos_x, pos_y))
        
        unmute_path = os.path.join(output_dir, "btn_mute_inactive.png")
        unmute_btn.save(unmute_path)
        print(f"Saved matched Unmute: {unmute_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

create_perfect_match_buttons()
