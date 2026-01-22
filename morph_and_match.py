import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
red_btn_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/btn_mute_active.png"
master_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

def get_body_w_h(img_pil):
    """
    Measure Width and Height of the 'Speaker Body' (left contiguous block).
    """
    arr = np.array(img_pil)
    if img_pil.mode == 'RGBA':
        mask = arr[:,:,3] > 10
    else:
        mask = arr > 10
        
    cols = np.any(mask, axis=0)
    if not np.any(cols): return 0, 0, (0,0,0,0)
    
    xmin, xmax_global = np.where(cols)[0][[0, -1]]
    
    # Body is left ~45%
    width_total = xmax_global - xmin
    cutoff = xmin + int(width_total * 0.45)
    
    mask_body = mask.copy()
    mask_body[:, cutoff:] = False
    
    rows = np.any(mask_body, axis=1)
    cols_b = np.any(mask_body, axis=0)
    
    if not np.any(rows): return 0, 0, (0,0,0,0)
    
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin_b, xmax_b = np.where(cols_b)[0][[0, -1]]
    
    h_body = ymax - ymin
    w_body = xmax_b - xmin_b
    
    return w_body, h_body, (xmin_b, ymin, xmax_b, ymax)

def morph_and_match():
    try:
    # 1. Measure Reference Body
        # To avoid measurement errors from overwrites/transparency, we use the KNOWN GOOD dimensions
        # from the user-approved state (Step 284).
        w_ref = 20
        h_ref = 32
        
        print(f"Reference Body (Hardcoded): W={w_ref}, H={h_ref}")

        # 2. Measure Master Icon Body
        img_clean = Image.open(master_icon_path).convert("RGBA")
        gray = img_clean.convert("L")
        icon_alpha = ImageOps.invert(gray)
        
        # Crop to full content first
        bbox_full = icon_alpha.getbbox()
        icon_cropped = img_clean.crop(bbox_full)
        icon_alpha_cropped = icon_alpha.crop(bbox_full)
        
        # Measure Body of this cropped icon
        w_src, h_src, bbox_src = get_body_w_h(icon_alpha_cropped)
        print(f"Source Body: W={w_src}, H={h_src}")
        
        # 3. Calculate Scaling Factors
        # We might need non-uniform scaling if shapes are truly different?
        # User said "Size is different". Usually means Height or Area.
        # Let's use uniform scaling based on HEIGHT, checking Width error.
        
        scale_h = h_ref / h_src
        scale_w = w_ref / w_src
        
        print(f"Scale H: {scale_h}, Scale W: {scale_w}")
        
        # If scales are close, use average? Or just force Height matching?
        # Let's match Height exactly, as that's visually dominant.
        scale = scale_h 
        
        # Resize the WHOLE icon by this scale
        w_c, h_c = icon_cropped.size
        new_w = int(w_c * scale)
        new_h = int(h_c * scale)
        
        icon_resized = icon_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        alpha_resized = icon_alpha_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Create "Perfect" Icon
        icon_perfect = Image.new("RGBA", (new_w, new_h), (0,0,0,0))
        # Wait, color depends on button.
        
        # 4. Generate BOTH buttons using this `icon_resized` geometry
        
        # --- Unmute (Forest Green + White Icon) ---
        forest_green = (34, 139, 34, 255) # ForestGreen #228B22
        
        # Use White Icon for better contrast on Green
        icon_white_unmute = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
        icon_white_unmute.putalpha(alpha_resized)
        
        unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_u = ImageDraw.Draw(unmute_btn)
        draw_u.rounded_rectangle((0, 0, 90, 70), radius=14, fill=forest_green)
        
        # Center
        cx = (90 - new_w) // 2
        cy = (70 - new_h) // 2
        unmute_btn.alpha_composite(icon_white_unmute, (cx, cy))
        
        unmute_btn.save(os.path.join(output_dir, "btn_mute_inactive.png"))
        print("Saved Unmute (Forest Green).")
        
        # --- Mute (Red + White Icon + Slash) ---
        # Note: We are RECREATING the Mute button here using the aligned icon.
        # This replaces the "Original" red button image content, but keeps the "Red Style".
        # This guarantees 100% match.
        
        red_bg_color = (204, 3, 2, 255)
        mute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_m = ImageDraw.Draw(mute_btn)
        draw_m.rounded_rectangle((0, 0, 90, 70), radius=14, fill=red_bg_color)
        
        icon_white = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
        icon_white.putalpha(alpha_resized)
        
        mute_btn.alpha_composite(icon_white, (cx, cy))
        
        # Draw Slash
        # Bottom-Left to Top-Right
        pad = 2
        x1 = cx - pad
        y1 = cy + new_h + pad
        x2 = cx + new_w + pad
        y2 = cy - pad
        
        draw_slash = ImageDraw.Draw(mute_btn)
        draw_slash.line([x1, y1, x2, y2], fill=(255, 255, 255, 255), width=5)
        
        mute_btn.save(os.path.join(output_dir, "btn_mute_active.png"))
        print("Saved Mute (Regenerated).")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

morph_and_match()
