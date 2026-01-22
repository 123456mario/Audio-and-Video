from PIL import Image
import os

src_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui_design_assets"
images = [
    "arrow_buttons_white_green_1765834662501.png",
    "zoom_buttons_white_green_1765834693420.png",
    "cam_front_buttons_white_green_1765834500487.png",
    "cam_side_buttons_white_green_1765834532463.png"
]

def get_row_bounds(img, y_start, y_end):
    row_img = img.crop((0, y_start, img.width, y_end))
    # Find all non-white pixels
    data = list(row_img.getdata())
    min_x, max_x = img.width, 0
    min_y, max_y = row_img.height, 0
    
    for i, p in enumerate(data):
        if p[0] < 240 or p[1] < 240 or p[2] < 240:
            x = i % img.width
            y = i // img.width
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    
    return min_x, min_y + y_start, max_x, max_y + y_start

for img_name in images:
    path = os.path.join(src_dir, img_name)
    img = Image.open(path).convert("RGBA")
    print(f"\n--- {img_name} ---")
    
    # Analyze Inactive Row (Top half approx)
    bx_in = get_row_bounds(img, 100, 512)
    print(f"Inactive Row Bounds: {bx_in}")
    
    # Analyze Active Row (Bottom half approx)
    bx_ac = get_row_bounds(img, 512, 900)
    print(f"Active Row Bounds: {bx_ac}")
