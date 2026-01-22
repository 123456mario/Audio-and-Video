import os
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
icon_speaker_path = os.path.join(brain_dir, "icon_speaker_black_1767929835911.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_ref_buttons(icon_path):
    try:
        # Load Icon (Black on Transparent or White)
        icon_img = Image.open(icon_path).convert("RGBA")
        
        # 1. Clean/Crop Icon
        gray = icon_img.convert("L")
        # Assuming icon is Black on White/Transparent.
        # If Black on White, Invert to get Mask.
        # If Transparent, Extract Alpha.
        # My generated icon is Black on White BG usually.
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
        
        # Prepare Icon Masks
        # Invert black icon to get white mask
        icon_mask = ImageOps.invert(icon_resized.convert("L"))
        
        # --- Unmute Button (Inactive) ---
        # "Matching color" -> Clean White/Grey look? Or Green?
        # Let's go with a very light grey/white background and dark grey icon.
        bg_unmute = (235, 235, 235, 255)
        icon_color_unmute = (50, 50, 50, 255)
        
        unmute_btn = Image.new("RGBA", (button_w, button_h), (0,0,0,0))
        draw_unmute = ImageDraw.Draw(unmute_btn)
        draw_unmute.rounded_rectangle((0, 0, button_w, button_h), radius=10, fill=bg_unmute) # slightly less rounded? Reference looks rounded.
        
        # Draw Icon
        icon_unmute_layer = Image.new("RGBA", (target_w, target_h), icon_color_unmute)
        icon_unmute_layer.putalpha(icon_mask)
        
        pos_x = (button_w - target_w) // 2
        pos_y = (button_h - target_h) // 2
        
        unmute_btn.alpha_composite(icon_unmute_layer, (pos_x, pos_y))
        
        unmute_path = os.path.join(output_dir, "btn_mute_inactive.png")
        unmute_btn.save(unmute_path)
        print(f"Saved: {unmute_path}")

        # --- Mute Button (Active) ---
        # Reference: Red BG, White Icon, Diagonal Slash.
        bg_mute = (200, 0, 0, 255) # Deep Red
        icon_color_mute = (255, 255, 255, 255) # White
        
        mute_btn = Image.new("RGBA", (button_w, button_h), (0,0,0,0))
        draw_mute = ImageDraw.Draw(mute_btn)
        draw_mute.rounded_rectangle((0, 0, button_w, button_h), radius=10, fill=bg_mute)
        
        # Draw Icon
        icon_mute_layer = Image.new("RGBA", (target_w, target_h), icon_color_mute)
        icon_mute_layer.putalpha(icon_mask)
        
        mute_btn.alpha_composite(icon_mute_layer, (pos_x, pos_y))
        
        # Draw Slash (White)
        # Check reference: Slash goes from bottom-left to top-right? Or Top-left to bottom-right?
        # Reference: Bottom-Left to Top-Right. ( / )
        # Usually Mute is ( \ ) or ( / ). Reference is ( / ).
        
        draw_slash = ImageDraw.Draw(mute_btn)
        
        # Coordinates for slash
        # Centered on icon
        # Size of slash should exceed icon slightly
        slash_w = width = 4
        pad = 2
        
        # Bottom-Left
        x1 = pos_x - pad
        y1 = pos_y + target_h + pad
        # Top-Right
        x2 = pos_x + target_w + pad
        y2 = pos_y - pad
        
        draw_slash.line([x1, y1, x2, y2], fill=(255, 255, 255, 255), width=4)
        
        mute_path = os.path.join(output_dir, "btn_mute_active.png")
        mute_btn.save(mute_path)
        print(f"Saved: {mute_path}")

    except Exception as e:
        print(f"Error processing: {e}")

create_ref_buttons(icon_speaker_path)
