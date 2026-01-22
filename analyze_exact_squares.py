from PIL import Image
import os

src_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui_design_assets/arrow_buttons_white_green_1765834662501.png"
img = Image.open(src_path).convert("RGBA")

def find_icon_box(img, start_x, start_y, end_x, end_y):
    # Ensure indices are within image
    start_x = max(0, start_x)
    start_y = max(0, start_y)
    end_x = min(img.width, end_x)
    end_y = min(img.height, end_y)
    
    box_img = img.crop((start_x, start_y, end_x, end_y))
    data = list(box_img.getdata())
    min_x, max_x = box_img.width, 0
    min_y, max_y = box_img.height, 0
    found = False
    for i, p in enumerate(data):
        # Using a higher threshold for "non-white" to avoid background noise if any
        if p[0] < 245 or p[1] < 245 or p[2] < 245:
            x = i % box_img.width
            y = i // box_img.width
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            found = True
    if not found: return None
    return (min_x + start_x, min_y + start_y, max_x + start_x, max_y + start_y)

print(f"--- Refined Analysis of {os.path.basename(src_path)} ---")
# 4 columns of 256 pixels each.
col_ranges = [(0, 255), (256, 511), (512, 767), (768, 1023)]
# Y ranges for the rows (avoiding the text labels as much as possible)
# Inactive state label is at top. Icons start below.
# Active state label is in middle. Icons start below.
row_ranges = [(200, 500), (550, 850)]

for r_idx, (r_start, r_end) in enumerate(row_ranges):
    state = "Inactive" if r_idx == 0 else "Active"
    for c_idx, (c_start, c_end) in enumerate(col_ranges):
        box = find_icon_box(img, c_start, r_start, c_end, r_end)
        if box:
            w, h = box[2]-box[0]+1, box[3]-box[1]+1
            print(f"{state} Icon {c_idx+1}: {box} (size {w}x{h})")

# Zoom: 2 columns of 512 pixels each
zoom_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui_design_assets/zoom_buttons_white_green_1765834693420.png"
img_z = Image.open(zoom_path).convert("RGBA")
print(f"\n--- Refined Analysis of {os.path.basename(zoom_path)} ---")
z_col_ranges = [(0, 511), (512, 1023)]
for r_idx, (r_start, r_end) in enumerate(row_ranges):
    state = "Inactive" if r_idx == 0 else "Active"
    for c_idx, (c_start, c_end) in enumerate(z_col_ranges):
        box = find_icon_box(img_z, c_start, r_start, c_end, r_end)
        if box:
            w, h = box[2]-box[0]+1, box[3]-box[1]+1
            print(f"{state} Icon {c_idx+1}: {box} (size {w}x{h})")
