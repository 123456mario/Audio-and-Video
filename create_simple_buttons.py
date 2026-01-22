import os
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
icon_speaker_path = os.path.join(brain_dir, "icon_speaker_black_1767929835911.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_simple_buttons(icon_path):
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
        # Target: Fits in 90x70. Scale 0.6
        button_w, button_h = 90, 70
        target_h = int(button_h * 0.6) 
        w, h = icon_cropped.size
        ratio = w / h
        target_w = int(target_h * ratio)
        
        if target_w > button_w * 0.8:
             target_w = int(button_w * 0.8)
             target_h = int(target_w / ratio)
             
        icon_resized = icon_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 3. Create Base Button (Unmute)
        # Light Grey Background
        bg_color = (255, 255, 255, 255) # White
        # Or maybe #F0F0F0?
        bg_color = (240, 240, 240, 255)
        
        base_button = Image.new("RGBA", (button_w, button_h), (0,0,0,0))
        draw = ImageDraw.Draw(base_button)
        draw.rounded_rectangle((0, 0, button_w, button_h), radius=15, fill=bg_color)
        
        # Paste Icon
        pos_x = (button_w - target_w) // 2
        pos_y = (button_h - target_h) // 2
        
        # Ensure icon is black
        icon_black = ImageOps.colorize(icon_resized.convert("L"), black="black", white="white") 
        # Wait, colorize maps 0 to black, 255 to white.
        # The icon source has Black on White.
        # We need Transparent background.
        # Use alpha mask from previous step
        icon_alpha = ImageOps.invert(icon_resized.convert("L"))
        final_icon = Image.new("RGBA", (target_w, target_h), (0,0,0,255))
        final_icon.putalpha(icon_alpha)
        
        base_button.alpha_composite(final_icon, (pos_x, pos_y))
        
        # Save Unmute (Inactive)
        unmute_path = os.path.join(output_dir, "btn_mute_inactive.png")
        base_button.save(unmute_path)
        print(f"Saved {unmute_path}")
        
        # 4. Create Mute Button (Active)
        # Exact same button, add Red Slash
        mute_button = base_button.copy()
        draw_mute = ImageDraw.Draw(mute_button)
        
        # Draw Red Slash
        # From top-left (ish) to bottom-right (ish) over the icon
        # Icon rect: pos_x, pos_y, pos_x+target_w, pos_y+target_h
        # Let's go a bit wider than icon
        pad = 5
        line_start = (pos_x - pad, pos_y - pad)
        line_end = (pos_x + target_w + pad, pos_y + target_h + pad)
        
        # Red Color #CC0000
        red_color = (204, 0, 0, 255)
        width = 6
        
        draw_mute.line([line_start, line_end], fill=red_color, width=width)
        
        # Save Mute (Active)
        mute_path = os.path.join(output_dir, "btn_mute_active.png")
        mute_button.save(mute_path)
        print(f"Saved {mute_path}")

    except Exception as e:
        print(f"Error processing: {e}")

create_simple_buttons(icon_speaker_path)
