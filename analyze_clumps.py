from PIL import Image
import os

def get_icon_boxes(img_path, row_starts):
    img = Image.open(img_path).convert("RGBA")
    width, height = img.size
    boxes = []
    
    # We expect 4 icons per row for ARROWS, 2 for ZOOM
    # Let's just find all clumps.
    for y_start, y_end in row_starts:
        # Scan row for clumps
        row_img = img.crop((0, y_start, width, y_end))
        data = list(row_img.getdata())
        
        # Simple clump finder: group columns that have any non-white pixels
        active_cols = []
        for x in range(width):
            has_content = False
            for y in range(row_img.height):
                p = row_img.getpixel((x, y))
                if p[0] < 245 or p[1] < 245 or p[2] < 245:
                    has_content = True
                    break
            if has_content:
                active_cols.append(x)
        
        # Group active columns into chunks (icons)
        if not active_cols: continue
        chunks = []
        current_chunk = [active_cols[0]]
        for i in range(1, len(active_cols)):
            if active_cols[i] - active_cols[i-1] > 10: # Gap of 10 pixels
                chunks.append(current_chunk)
                current_chunk = [active_cols[i]]
            else:
                current_chunk.append(active_cols[i])
        chunks.append(current_chunk)
        
        # For each chunk, find the exact vertical bounds
        for chunk in chunks:
            x_min, x_max = min(chunk), max(chunk)
            # Filter out very small chunks (could be noise or text)
            if x_max - x_min < 50: continue
            
            # Now find y bounds for this x range
            y_min, y_max = row_img.height, 0
            for x in range(x_min, x_max + 1):
                for y in range(row_img.height):
                    p = row_img.getpixel((x, y))
                    if p[0] < 245 or p[1] < 245 or p[2] < 245:
                        y_min = min(y_min, y)
                        y_max = max(y_max, y)
            
            # Global coordinates
            # Add padding
            pad = 5
            boxes.append((
                max(0, x_min - pad),
                max(0, y_min + y_start - pad),
                min(width, x_max + pad),
                min(height, y_max + y_start + pad)
            ))
    return boxes

# Analysis
src_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui_design_assets"

# PTZ Arrows
ptz_path = os.path.join(src_dir, "arrow_buttons_white_green_1765834662501.png")
ptz_boxes = get_icon_boxes(ptz_path, [(200, 500), (550, 850)])
print(f"PTZ Boxes ({len(ptz_boxes)}):")
for b in ptz_boxes: print(f"  {b} size {b[2]-b[0]}x{b[3]-b[1]}")

# Zoom
zoom_path = os.path.join(src_dir, "zoom_buttons_white_green_1765834693420.png")
zoom_boxes = get_icon_boxes(zoom_path, [(200, 550), (550, 900)])
print(f"\nZoom Boxes ({len(zoom_boxes)}):")
for b in zoom_boxes: print(f"  {b} size {b[2]-b[0]}x{b[3]-b[1]}")

# Cam Front
front_path = os.path.join(src_dir, "cam_front_buttons_white_green_1765834500487.png")
front_boxes = get_icon_boxes(front_path, [(200, 500), (500, 900)])
print(f"\nCam Front Boxes ({len(front_boxes)}):")
for b in front_boxes: print(f"  {b} size {b[2]-b[0]}x{b[3]-b[1]}")

# Cam Side
side_path = os.path.join(src_dir, "cam_side_buttons_white_green_1765834532463.png")
side_boxes = get_icon_boxes(side_path, [(100, 500), (500, 900)])
print(f"\nCam Side Boxes ({len(side_boxes)}):")
for b in side_boxes: print(f"  {b} size {b[2]-b[0]}x{b[3]-b[1]}")
