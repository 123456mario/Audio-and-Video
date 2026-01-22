import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
red_btn_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/btn_mute_active.png" # Current Red Button
master_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png") # Clean Icon Source
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

def get_speaker_body_height(img_pil):
    """
    Heuristic to find the height of the 'Speaker Body' (the left solid block).
    It scans columns from left to right. The first block of non-transparent/white pixels
    is considered the body.
    """
    arr = np.array(img_pil)
    # Convert to binary mask (True = Content)
    # If RGBA, check Alpha > 10. If RGB, Check Intensity?
    if img_pil.mode == 'RGBA':
        mask = arr[:,:,3] > 10
    elif img_pil.mode == 'L':
         mask = arr > 10
    else:
        # Assume white on black or black on white?
        # Let's assume content is non-white
        mask = np.mean(arr, axis=2) < 250
        
    # Isolate content columns
    cols = np.any(mask, axis=0)
    if not np.any(cols):
        return 0, 0, 0
    
    # Find start and end of "Body"
    # Typically body is the first contiguous block.
    # But usually there is a tiny gap between body and waves? Not always.
    # Let's just find the max height in the left 50% of the content.
    
    # Crop to content first
    rows = np.any(mask, axis=1)
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    
    content_width = xmax - xmin
    mid_x_global = xmin + content_width // 2
    
    # Search max height in left half
    # Let's iterate columns from xmin to mid_x_global
    max_h = 0
    for x in range(xmin, mid_x_global + 1):
        col_mask = mask[:, x]
        if np.any(col_mask):
            ys = np.where(col_mask)[0]
            h = ys[-1] - ys[0]
            if h > max_h:
                max_h = h
                
    return max_h, mask, (xmin, ymin, xmax, ymax)

def finalize_buttons():
    try:
        # --- 1. Analyze Red Button (Reference) ---
        img_red = Image.open(red_btn_path).convert("RGBA")
        
        # Isolate Content (White Mask)
        arr_red = np.array(img_red)
        r, g, b = arr_red[:,:,0], arr_red[:,:,1], arr_red[:,:,2]
        # Content is White pixels (Icon + Slash)
        content_mask = (r > 200) & (g > 200) & (b > 200)
        
        # Create a temp image of just the content to measure
        h_red, mask_red, bbox_red = get_speaker_body_height(img_red) # This function might need tweaking for Red BG
        
        # Let's do custom extraction for Red Btn
        # Content BBox
        rows = np.any(content_mask, axis=1)
        cols = np.any(content_mask, axis=0)
        
        if not np.any(rows):
             print("Error: No content found in Red Button.")
             return

        ymin_r, ymax_r = np.where(rows)[0][[0, -1]]
        xmin_r, xmax_r = np.where(cols)[0][[0, -1]]
        
        content_red = img_red.crop((xmin_r, ymin_r, xmax_r+1, ymax_r+1))
        
        # Measure Body Height in Red Button
        # The body is the left part.
        w_cr, h_cr = content_red.size
        # Left 40%
        left_part = content_red.crop((0, 0, int(w_cr*0.4), h_cr))
        # Find height of non-transparent (or white) pixels
        arr_lp = np.array(left_part)
        # Check for white pixels
        mask_lp = (arr_lp[:,:,0] > 200)
        if np.any(mask_lp):
             rows_lp = np.any(mask_lp, axis=1)
             ym_lp, yM_lp = np.where(rows_lp)[0][[0, -1]]
             body_height_red = yM_lp - ym_lp
        else:
             body_height_red = h_cr # Fallback
             
        print(f"Red Button Body Height: {body_height_red}")
        
        # --- 2. Re-create Red Button (Centered) ---
        # Create new Red BG
        red_bg_color = (204, 3, 2, 255) # Sampled approximate red
        new_mute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_m = ImageDraw.Draw(new_mute_btn)
        draw_m.rounded_rectangle((0, 0, 90, 70), radius=14, fill=red_bg_color)
        
        # Paste centered
        c_x = (90 - w_cr) // 2
        c_y = (70 - h_cr) // 2
        new_mute_btn.alpha_composite(content_red, (c_x, c_y))
        
        new_mute_btn.save(os.path.join(output_dir, "btn_mute_active.png"))
        print("Saved centered Mute.")

        # --- 3. Process Unmute Icon (Matching Scale) ---
        img_clean = Image.open(master_icon_path).convert("RGBA")
        gray = img_clean.convert("L")
        icon_alpha = ImageOps.invert(gray)
        bbox_i = icon_alpha.getbbox()
        icon_cropped = img_clean.crop(bbox_i)
        
        # Measure Body Height in Clean Icon
        w_cc, h_cc = icon_cropped.size
        left_part_c = icon_cropped.crop((0, 0, int(w_cc*0.4), h_cc))
        arr_lpc = np.array(left_part_c)
        # It's black on white, so body is black (low values)
        # Wait, we loaded img_clean (black on white).
        mask_lpc = np.mean(arr_lpc[:,:,:3], axis=2) < 100
        
        if np.any(mask_lpc):
             rows_lpc = np.any(mask_lpc, axis=1)
             ym_lpc, yM_lpc = np.where(rows_lpc)[0][[0, -1]]
             body_height_clean = yM_lpc - ym_lpc
        else:
             body_height_clean = h_cc
             
        print(f"Clean Icon Body Height: {body_height_clean}")
        
        # Calculate Scale
        scale = body_height_red / body_height_clean
        print(f"Scale Factor: {scale}")
        
        # Resize Icon
        new_w_icon = int(w_cc * scale)
        new_h_icon = int(h_cc * scale)
        
        # We need the alpha mask for the new icon
        icon_alpha_cropped = icon_alpha.crop(bbox_i)
        icon_alpha_resized = icon_alpha_cropped.resize((new_w_icon, new_h_icon), Image.Resampling.LANCZOS)
        
        # Create Dark Icon
        icon_final = Image.new("RGBA", (new_w_icon, new_h_icon), (50, 50, 50, 255))
        icon_final.putalpha(icon_alpha_resized)
        
        # --- 4. Create Unmute Button (Centered) ---
        new_unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_u = ImageDraw.Draw(new_unmute_btn)
        draw_u.rounded_rectangle((0, 0, 90, 70), radius=14, fill=(235, 235, 235, 255))
        
        # Center
        c_x_u = (90 - new_w_icon) // 2
        c_y_u = (70 - new_h_icon) // 2
        
        new_unmute_btn.alpha_composite(icon_final, (c_x_u, c_y_u))
        
        new_unmute_btn.save(os.path.join(output_dir, "btn_mute_inactive.png"))
        print("Saved centered/scaled Unmute.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

finalize_buttons()
