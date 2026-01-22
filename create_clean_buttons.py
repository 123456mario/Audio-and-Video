import os
from PIL import Image, ImageDraw, ImageOps, ImageChops

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
icon_speaker_path = os.path.join(brain_dir, "icon_speaker_black_1767929835911.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_clean_buttons(icon_path):
    try:
        # Load Icon
        icon_img = Image.open(icon_path).convert("RGBA")
        
        # 1. Clean/Crop Icon
        gray = icon_img.convert("L")
        inverted_gray = ImageOps.invert(gray.convert("RGB")).convert("L") 
        mask = inverted_gray.point(lambda p: 255 if p > 50 else 0)
        bbox = mask.getbbox()
        
        if bbox:
            icon_cropped = icon_img.crop(bbox)
        else:
            icon_cropped = icon_img

        # 2. Resize Icon
        button_w, button_h = 90, 70
        target_h = int(button_h * 0.6) 
        w, h = icon_cropped.size
        ratio = w / h
        target_w = int(target_h * ratio)
        
        if target_w > button_w * 0.8:
             target_w = int(button_w * 0.8)
             target_h = int(target_w / ratio)
             
        icon_resized = icon_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 3. Create Buttons
        bg_color = (255, 255, 255, 255) 
        
        # --- Unmute (Waves Visible) ---
        unmute_button = Image.new("RGBA", (button_w, button_h), (0,0,0,0))
        draw_unmute = ImageDraw.Draw(unmute_button)
        draw_unmute.rounded_rectangle((0, 0, button_w, button_h), radius=15, fill=bg_color)
        
        # Icon mask
        icon_alpha = ImageOps.invert(icon_resized.convert("L"))
        unmute_icon = Image.new("RGBA", (target_w, target_h), (0,0,0,255))
        unmute_icon.putalpha(icon_alpha)
        
        pos_x = (button_w - target_w) // 2
        pos_y = (button_h - target_h) // 2
        
        unmute_button.alpha_composite(unmute_icon, (pos_x, pos_y))
        
        unmute_path = os.path.join(output_dir, "btn_mute_inactive.png")
        unmute_button.save(unmute_path)
        print(f"Saved Unmute: {unmute_path}")

        # --- Mute (Waves Hidden) ---
        # Mask out right 45% of width
        mute_icon = unmute_icon.copy()
        
        eraser = Image.new("L", (target_w, target_h), 255) # White = Keep
        draw_eraser = ImageDraw.Draw(eraser)
        # Erase right side (Waves)
        draw_eraser.rectangle((int(target_w * 0.55), 0, target_w, target_h), fill=0) # Black = Drop
        
        # Combine alpha channels
        # mute_icon.alpha = mute_icon.alpha * eraser
        current_alpha = mute_icon.getchannel("A")
        new_alpha = ImageChops.multiply(current_alpha, eraser)
        mute_icon.putalpha(new_alpha)
        
        mute_button_bg = Image.new("RGBA", (button_w, button_h), (0,0,0,0))
        draw_mute_bg = ImageDraw.Draw(mute_button_bg)
        draw_mute_bg.rounded_rectangle((0, 0, button_w, button_h), radius=15, fill=bg_color)
        
        mute_button_bg.alpha_composite(mute_icon, (pos_x, pos_y))
        
        mute_path = os.path.join(output_dir, "btn_mute_active.png")
        mute_button_bg.save(mute_path)
        print(f"Saved Mute: {mute_path}")

    except Exception as e:
        print(f"Error processing: {e}")

create_clean_buttons(icon_speaker_path)
