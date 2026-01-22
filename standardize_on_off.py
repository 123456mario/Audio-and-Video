import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

# Paths
base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"
master_blank_path = os.path.join(base_dir, "btn_off_blank.png")
# Use Regular Arial for thinner text
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"

def standardize():
    try:
        # Load Master (White Crystal Button)
        img_master_raw = Image.open(master_blank_path).convert("RGBA")
        
        # --- IMPROVED CLEANING STEP ---
        # 1. Brightness Clamping: "White" button should not have pitch black pixels.
        # Lift all dark pixels to be at least Light Grey (e.g. 180,180,180).
        # This turns "Black Borders" into "Light Grey/White", making them invisible.
        arr = np.array(img_master_raw)
        r, g, b, a = arr.T
        
        # Define minimum brightness (Lift Blacks)
        min_val = 160 
        r[:] = np.maximum(r, min_val)
        g[:] = np.maximum(g, min_val)
        b[:] = np.maximum(b, min_val)
        
        # Re-assemble
        img_clean_base = Image.fromarray(arr)
        
        # 2. Geometric Edge Cleaning (Soft Mask)
        # Generate a perfect rounded rectangle mask to cut off fuzzy edges
        width, height = img_clean_base.size
        print(f"Master Size: {width}x{height}")
        
        mask = Image.new("L", (width, height), 0)
        draw_mask = ImageDraw.Draw(mask)
        # Assume 100x100 button has slight padding? Or full fill?
        # Let's preserve full size but mask edges. 
        # Button likely fills the square.
        draw_mask.rounded_rectangle((0, 0, width, height), radius=16, fill=255)
        
        # Apply mask (use minimum of existing alpha and new mask)
        # ImageChops.darker(img1, img2) returns min(img1, img2)
        img_master = img_clean_base.copy()
        new_alpha = ImageChops.darker(img_clean_base.split()[3], mask)
        img_master.putalpha(new_alpha)
        
        # Font Setup
        try:
            # Slightly larger size since it is thinner
            font = ImageFont.truetype(font_path, 36)
        except:
            font = ImageFont.load_default()
            
        # --- 1. Create OFF Button (White) ---
        img_off = img_master.copy()
        draw_off = ImageDraw.Draw(img_off)
        
        # Draw "OFF" Text (Black)
        text_off = "OFF"
        # Calculate text size using bbox
        bbox_off = draw_off.textbbox((0, 0), text_off, font=font)
        w_text_off = bbox_off[2] - bbox_off[0]
        h_text_off = bbox_off[3] - bbox_off[1]
        
        # Strict centering
        x_off = (width - w_text_off) // 2
        y_off = (height - h_text_off) // 2
        
        # Draw with anchor? No, standard xy is top-left of bbox? 
        # Actually textbbox returns coords relative to (0,0). 
        # PIL draw.text draws at top-left.
        # But text has ascenders/descenders. 
        # Ideally use anchor="mm" (middle-middle) if available in this PIL version?
        # Let's try anchor="mm" for perfect centering.
        x_center = width // 2
        y_center = height // 2
        draw_off.text((x_center, y_center), text_off, font=font, fill="black", anchor="mm")
        
        off_path = os.path.join(base_dir, "btn_off_text.png")
        img_off.save(off_path)
        print(f"Saved: {off_path}")
        
        # --- 2. Create ON Button (Green) ---
        # Strategy: RGB -> Grayscale -> Colorize
        gray = img_master.convert("L")
        img_green_base = ImageOps.colorize(gray, black="black", white="#00DD00") 
        
        img_green = img_green_base.convert("RGBA")
        # Restore Alpha from Master
        img_green.putalpha(img_master.split()[3])
        
        # Save Blank Green Button
        on_blank_path = os.path.join(base_dir, "btn_on_blank.png")
        img_green.save(on_blank_path)
        print(f"Saved: {on_blank_path}")
        
        draw_on = ImageDraw.Draw(img_green)
        
        # Draw "ON" Text (Black)
        text_on = "ON"
        draw_on.text((x_center, y_center), text_on, font=font, fill="black", anchor="mm")
        
        on_path = os.path.join(base_dir, "btn_on_text.png")
        img_green.save(on_path)
        print(f"Saved: {on_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

standardize()
