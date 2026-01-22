import os
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
original_ref_path = os.path.join(brain_dir, "uploaded_image_1767930732903.png")
cleaned_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_final_buttons():
    try:
        # --- 1. Mute Button (From Original Reference) ---
        img_ref = Image.open(original_ref_path).convert("RGBA")
        
        # Crop to the Red Button (remove whitespace)
        # Find bbox of non-white pixels? Or non-transparent?
        # The reference might have white space.
        bg = Image.new("RGBA", img_ref.size, (255,255,255,255))
        diff = ImageChops.difference(img_ref, bg)
        bbox = diff.getbbox()
        
        # If difference extraction fails (e.g. no alpha), try finding the Red Box.
        # Simple threshold on Red channel?
        # Let's just use standard crop.
        if bbox:
            img_ref_cropped = img_ref.crop(bbox)
        else:
             # Try cropping to color logic
             # Check distinct red color? 
             # Let's assume standard bbox works or just resize directly if it looks tight.
             # Actually, let's just resize directly. Usually uploaded images are tight or have minimal padding.
             img_ref_cropped = img_ref
             
        # Resize to 90x70
        mute_btn = img_ref_cropped.resize((90, 70), Image.Resampling.LANCZOS)
        
        mute_path = os.path.join(output_dir, "btn_mute_active.png")
        mute_btn.save(mute_path)
        print(f"Saved Mute: {mute_path}")

        # --- 2. Unmute Button (From Cleaned AI Generation) ---
        # Load Clean Icon
        img_clean = Image.open(cleaned_icon_path).convert("RGBA")
        
        # Extract Icon (Black)
        # It's likely Black on White.
        gray = img_clean.convert("L")
        # Invert to get alpha mask (White parts become black opacity, Black parts become White opacity)
        # We want Black parts (Icon) to be opaque.
        # Source is White BG (255), Black Icon (0).
        # Invert -> BG (0), Icon (255). Perfect alpha mask.
        icon_alpha = ImageOps.invert(gray)
        
        # Crop tight to icon
        bbox_icon = icon_alpha.getbbox()
        if bbox_icon:
            icon_clean_cropped = img_clean.crop(bbox_icon)
            icon_alpha_cropped = icon_alpha.crop(bbox_icon)
        else:
            icon_clean_cropped = img_clean
            icon_alpha_cropped = icon_alpha
            
        # Create Icon Layer (Black or Dark Grey)
        # User requested "matching color".
        # Let's use a Dark Grey #333333
        icon_w, icon_h = icon_clean_cropped.size
        icon_layer = Image.new("RGBA", (icon_w, icon_h), (50, 50, 50, 255))
        icon_layer.putalpha(icon_alpha_cropped)
        
        # Resize Icon to match the scale of the Mute button icon
        # Roughly 60% of button height
        target_h = int(70 * 0.6) # 42px
        ratio = icon_w / icon_h
        target_w = int(target_h * ratio)
        
        icon_final = icon_layer.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Create Background (Light Grey)
        # Match the shape of Mute button?
        # Standard Rounded Rect 90x70
        unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw = ImageDraw.Draw(unmute_btn)
        draw.rounded_rectangle((0, 0, 90, 70), radius=12, fill=(235, 235, 235, 255))
        
        # Center Icon
        pos_x = (90 - target_w) // 2
        pos_y = (70 - target_h) // 2
        
        unmute_btn.alpha_composite(icon_final, (pos_x, pos_y))
        
        unmute_path = os.path.join(output_dir, "btn_mute_inactive.png")
        unmute_btn.save(unmute_path)
        print(f"Saved Unmute: {unmute_path}")

    except Exception as e:
        print(f"Error processing: {e}")
        import traceback
        traceback.print_exc()

import PIL.ImageChops as ImageChops # Import needed for bbox logic
create_final_buttons()
