import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
# We use the CLEANED icon as the master source for BOTH buttons to ensure identical geometry.
# Even though it's AI generated, it's consistent.
# The user wants "One type" of speaker image.
master_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png")
original_ref_path = os.path.join(brain_dir, "uploaded_image_1767930732903.png") # Just for color reference
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_uniform_buttons():
    try:
        # 1. Get Colors from Original Reference
        img_ref = Image.open(original_ref_path).convert("RGB")
        arr = np.array(img_ref)
        # Find dominant Red color
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        mask = (r > 150) & (g < 100) & (b < 100)
        if np.any(mask):
            red_pixels = arr[mask]
            # Average color
            avg_red = np.mean(red_pixels, axis=0).astype(int)
            red_bg_color = tuple(avg_red) + (255,)
            print(f"Detected Red Color: {red_bg_color}")
        else:
            red_bg_color = (200, 0, 0, 255) # Fallback

        # 2. Prepare Master Icon
        img_master = Image.open(master_icon_path).convert("RGBA")
        
        # Extract Icon Mask
        # Source is White BG, Black Icon.
        # Gray -> Invert -> Alpha
        gray = img_master.convert("L")
        icon_alpha = ImageOps.invert(gray)
        
        # Crop tight
        bbox = icon_alpha.getbbox()
        if bbox:
            alpha_cropped = icon_alpha.crop(bbox)
        else:
            alpha_cropped = icon_alpha
            
        # Determine Icon Size
        # 90x70 button. Icon height approx 42px (60%)
        # But let's check exact crop ratio
        target_h = int(70 * 0.6)
        w, h = alpha_cropped.size
        ratio = w / h
        target_w = int(target_h * ratio)
        
        # Resize Alpha Mask
        alpha_final = alpha_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 3. Create Unmute Button
        # Light Grey BG, Dark Grey Icon
        unmute_bg_color = (235, 235, 235, 255)
        # Use corner radius 14 to match the look
        
        unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_un = ImageDraw.Draw(unmute_btn)
        draw_un.rounded_rectangle((0, 0, 90, 70), radius=14, fill=unmute_bg_color)
        
        # Icon Layer
        icon_dark = Image.new("RGBA", (target_w, target_h), (50, 50, 50, 255))
        icon_dark.putalpha(alpha_final)
        
        # Center
        pos_x = (90 - target_w) // 2
        pos_y = (70 - target_h) // 2
        
        unmute_btn.alpha_composite(icon_dark, (pos_x, pos_y))
        unmute_btn.save(os.path.join(output_dir, "btn_mute_inactive.png"))
        print("Saved uniform Unmute.")
        
        # 4. Create Mute Button
        # Red BG, White Icon, White Slash
        mute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_mu = ImageDraw.Draw(mute_btn)
        draw_mu.rounded_rectangle((0, 0, 90, 70), radius=14, fill=red_bg_color)
        
        # Icon Layer (White)
        icon_white = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))
        icon_white.putalpha(alpha_final)
        
        mute_btn.alpha_composite(icon_white, (pos_x, pos_y))
        
        # Draw Slash
        # Reference: Bottom-Left to Top-Right.
        # Length: Covers icon + padding
        pad = 2
        x1 = pos_x - pad
        y1 = pos_y + target_h + pad
        x2 = pos_x + target_w + pad
        y2 = pos_y - pad
        
        draw_slash = ImageDraw.Draw(mute_btn)
        draw_slash.line([x1, y1, x2, y2], fill=(255, 255, 255, 255), width=5) # Slightly thicker?
        
        mute_btn.save(os.path.join(output_dir, "btn_mute_active.png"))
        print("Saved uniform Mute.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

create_uniform_buttons()
