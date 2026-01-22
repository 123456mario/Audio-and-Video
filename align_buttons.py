import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
red_btn_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/btn_mute_active.png" # The "Master" Red Button
master_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png") # Clean Icon Source
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

def match_by_waves():
    try:
        # 1. Analyze Red Button (Target)
        img_red = Image.open(red_btn_path).convert("RGBA")
        arr_red = np.array(img_red)
        
        # Mask White Pixels (The Icon + Slash) on Red BG
        # R>200, G>200, B>200
        r, g, b = arr_red[:,:,0], arr_red[:,:,1], arr_red[:,:,2]
        white_mask = (r > 200) & (g > 200) & (b > 200)
        
        # We want the "Waves". They are likely the right-most components.
        # Let's find the bounding box of the *entire* white content first for sanity
        rows = np.any(white_mask, axis=1)
        cols = np.any(white_mask, axis=0)
        if not np.any(rows):
            print("No white pixels found in Red Button!")
            return
            
        # Isolate Waves:
        # The waves are typically on the right side.
        # Let's look at the columns from Right to Left.
        # Find the first block of white pixels columns, then a gap, then the speaker body.
        
        col_indices = np.where(cols)[0]
        # Iterate from right (max index) to left
        # Group contiguous columns
        # ... simplified: split image in half vertically?
        # Waves are usually in the right half.
        mid_x = img_red.width // 2
        
        # Mask only right half
        waves_mask = white_mask.copy()
        waves_mask[:, :mid_x] = False # Clear left side
        
        # Get BBox of Waves
        rows_w = np.any(waves_mask, axis=1)
        cols_w = np.any(waves_mask, axis=0)
        
        if not np.any(rows_w):
             print("Could not isolate waves in Red Button. Fallback to full fit?")
             # Fallback: Just use full height matching (roughly)
             full_height = np.where(rows)[0][-1] - np.where(rows)[0][0]
             target_h_icon = int(full_height * 0.9) # Assume slash adds 10%
             # ...
             return

        ymin_w, ymax_w = np.where(rows_w)[0][[0, -1]]
        xmin_w, xmax_w = np.where(cols_w)[0][[0, -1]]
        
        wave_height_red = ymax_w - ymin_w
        wave_width_red = xmax_w - xmin_w
        wave_center_y_red = (ymin_w + ymax_w) / 2
        wave_right_x_red = xmax_w # Align to right edge of waves?
        
        print(f"Red Waves: H={wave_height_red}, W={wave_width_red} at Y={wave_center_y_red}")

        # 2. Analyze Clean Icon (Source)
        img_clean = Image.open(master_icon_path).convert("RGBA")
        gray = img_clean.convert("L")
        # Invert to get White Icon on Black
        icon_white = ImageOps.invert(gray)
        arr_icon = np.array(icon_white)
        icon_mask = arr_icon > 128
        
        # Find Waves in Clean Icon
        mid_x_icon = img_clean.width // 2
        
        # Logic: Find center of mass of icon, look right?
        # Let's just crop to icon bbox first
        r_i = np.any(icon_mask, axis=1)
        c_i = np.any(icon_mask, axis=0)
        y1, y2 = np.where(r_i)[0][[0, -1]]
        x1, x2 = np.where(c_i)[0][[0, -1]]
        
        # Crop to content
        icon_cropped = icon_white.crop((x1, y1, x2, y2))
        
        # Now find waves in cropped icon
        # Again, look at right half relative to its own width
        w_c, h_c = icon_cropped.size
        arr_c = np.array(icon_cropped)
        mask_c = arr_c > 128
        
        waves_mask_c = mask_c.copy()
        waves_mask_c[:, :int(w_c*0.6)] = False # Clear left 60% (Speaker body is usually large)
        
        r_wc = np.any(waves_mask_c, axis=1)
        if not np.any(r_wc):
            print("Could not find waves in Source Icon!")
            return
            
        ymin_wc, ymax_wc = np.where(r_wc)[0][[0, -1]]
        wave_height_clean = ymax_wc - ymin_wc
        
        # 3. Calculate Scaling
        scale = wave_height_red / wave_height_clean
        print(f"Calculated Scale: {scale}")
        
        # Resize Icon
        new_w = int(w_c * scale)
        new_h = int(h_c * scale)
        icon_resized = icon_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 4. Create Unmute Button with aligned icon
        # We need to position it such that the waves align.
        # Red Waves Center Y -> wave_center_y_red
        # Resized Icon Waves Center Y -> (ymin_wc * scale + ymax_wc * scale) / 2?
        # No, ymin_wc is relative to the cropped icon top.
        # Let's find waves center in the resized icon.
        
        # Recalculate waves center in resized icon (It's linear scaling)
        wave_center_y_clean_local = (ymin_wc + ymax_wc) / 2
        wave_center_y_resized = wave_center_y_clean_local * scale
        
        # We want 'wave_center_y_resized' to be at 'wave_center_y_red' in the final 90x70 image.
        # Top of Icon (y) = wave_center_y_red - wave_center_y_resized
        
        target_y = int(wave_center_y_red - wave_center_y_resized)
        
        # For X alignment:
        # Align Right Edge of Waves?
        # Red Waves Right X = xmax_w
        # Resized Icon Waves Right X (relative to icon left) = xmax_wc * scale
        # where xmax_wc is relative to cropped icon.
        # Actually xmax_wc is the rightmost pixel of waves in cropped icon. Which is just new_w roughly.
        
        c_wc = np.any(waves_mask_c, axis=0) # columns of waves in cropped
        xmax_wc_local = np.where(c_wc)[0][-1]
        
        wave_right_x_resized = xmax_wc_local * scale
        
        target_x = int(wave_right_x_red - wave_right_x_resized)
        
        print(f"Placing icon at {target_x}, {target_y}")
        
        # Create Button
        bg_color = (235, 235, 235, 255)
        unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw = ImageDraw.Draw(unmute_btn)
        draw.rounded_rectangle((0, 0, 90, 70), radius=14, fill=bg_color)
        
        # Create Dark Icon Layer
        icon_layer = Image.new("RGBA", (new_w, new_h), (50, 50, 50, 255))
        icon_layer.putalpha(icon_resized)
        
        unmute_btn.alpha_composite(icon_layer, (target_x, target_y))
        
        path = os.path.join(output_dir, "btn_mute_inactive.png")
        unmute_btn.save(path)
        print(f"Saved aligned Unmute: {path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

match_by_waves()
