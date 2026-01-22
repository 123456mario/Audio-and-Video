import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
red_btn_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/btn_mute_active.png"
master_icon_path = os.path.join(brain_dir, "ref_cleaned_unmute_1767930899756.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

def get_body_bbox(img_pil):
    """
    Returns the bounding box (xmin, ymin, xmax, ymax) of the 'Speaker Body'.
    Assumes Speaker Body is the left-most content.
    """
    arr = np.array(img_pil)
    if img_pil.mode == 'RGBA':
        mask = arr[:,:,3] > 10
    else:
        mask = arr > 10
        
    cols = np.any(mask, axis=0)
    if not np.any(cols): return None
    
    xmin, xmax_global = np.where(cols)[0][[0, -1]]
    
    # Body is left part. Let's take the first continuous block of columns?
    # Or just left 40% of the total width?
    width = xmax_global - xmin
    cutoff = xmin + int(width * 0.45) # 45% should cover body, exclude waves
    
    # Analyze columns up to cutoff
    # Find ymin, ymax within this region
    
    mask_body = mask.copy()
    mask_body[:, cutoff:] = False # Clear right side
    
    rows = np.any(mask_body, axis=1)
    cols_b = np.any(mask_body, axis=0)
    
    if not np.any(rows): return None
    
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin_b, xmax_b = np.where(cols_b)[0][[0, -1]]
    
    return (xmin_b, ymin, xmax_b, ymax)

def align_anchor():
    try:
        # 1. Analyze Red Button (Fixed Reference)
        img_red = Image.open(red_btn_path).convert("RGBA")
        
        # Identify Body Rect using content mask logic (Red BG handling)
        arr_red = np.array(img_red)
        # Content is white-ish
        content_mask = (arr_red[:,:,0] > 150) & (arr_red[:,:,1] > 150) & (arr_red[:,:,2] > 150)
        
        # Create temp image for analysis
        img_content_red = Image.fromarray(content_mask.astype(np.uint8)*255)
        
        bbox_body_red = get_body_bbox(img_content_red)
        if not bbox_body_red:
            print("Failed to find body in Red Button")
            return
            
        print(f"Red Body BBox: {bbox_body_red}")
        h_body_red = bbox_body_red[3] - bbox_body_red[1]
        
        # 2. Prepare Clean Icon
        img_clean = Image.open(master_icon_path).convert("RGBA")
        gray = img_clean.convert("L")
        icon_alpha = ImageOps.invert(gray)
        
        # Crop tight to full icon first
        bbox_full = icon_alpha.getbbox()
        icon_cropped = img_clean.crop(bbox_full)
        icon_alpha_cropped = icon_alpha.crop(bbox_full)
        
        # Analyze Body of Clean Icon
        img_clean_mask = icon_alpha_cropped # It's a mask already
        bbox_body_clean = get_body_bbox(img_clean_mask)
        if not bbox_body_clean:
            print("Failed to find body in Clean Icon")
            return
            
        print(f"Clean Body BBox: {bbox_body_clean}")
        h_body_clean = bbox_body_clean[3] - bbox_body_clean[1]
        
        # 3. Scale Clean Icon
        scale = h_body_red / h_body_clean
        print(f"Scale: {scale}")
        
        w_c, h_c = icon_cropped.size
        new_w = int(w_c * scale)
        new_h = int(h_c * scale)
        
        icon_resized = icon_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        alpha_resized = icon_alpha_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Create Dark Icon using Alpha
        icon_final = Image.new("RGBA", (new_w, new_h), (50, 50, 50, 255))
        icon_final.putalpha(alpha_resized)
        
        # 4. Calculate Position to Align Bodies
        # We want: 
        # Position_Unmute_Body_TopLeft_in_Canvas == Position_Red_Body_TopLeft_in_Canvas
        
        # Red Body TopLeft in Canvas: (bbox_body_red[0], bbox_body_red[1])
        target_x = bbox_body_red[0]
        target_y = bbox_body_red[1]
        
        # Clean Body TopLeft in Resized Icon (Relative to Icon 0,0)
        # We need to scale the bbox_body_clean coordinates
        clean_x_rel = bbox_body_clean[0] * scale
        clean_y_rel = bbox_body_clean[1] * scale
        
        # Calculate Canvas Coordinates for Icon TopLeft
        # Icon_X + clean_x_rel = target_x
        # Icon_Y + clean_y_rel = target_y
        
        final_x = int(target_x - clean_x_rel)
        final_y = int(target_y - clean_y_rel)
        
        print(f"Aligning Unmute Icon at: ({final_x}, {final_y})")
        
        # 5. Create Unmute Button
        new_unmute_btn = Image.new("RGBA", (90, 70), (0,0,0,0))
        draw_u = ImageDraw.Draw(new_unmute_btn)
        draw_u.rounded_rectangle((0, 0, 90, 70), radius=14, fill=(235, 235, 235, 255))
        
        new_unmute_btn.alpha_composite(icon_final, (final_x, final_y))
        
        new_unmute_btn.save(os.path.join(output_dir, "btn_mute_inactive.png"))
        print("Saved aligned Unmute.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

align_anchor()
