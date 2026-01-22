from PIL import Image
import os

src_path = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui_design_assets/arrow_buttons_white_green_1765834662501.png"
img = Image.open(src_path).convert("RGBA")

def find_square_top(img, x_range, y_search_range):
    # Find a horizontal line of at least 50px of similar color
    for y in range(y_search_range[0], y_search_range[1]):
        consecutive = 0
        for x in range(x_range[0], x_range[1]):
            p = img.getpixel((x, y))
            if p[0] < 240 or p[1] < 240 or p[2] < 240:
                consecutive += 1
                if consecutive > 80: # A clear horizontal line
                    return y
            else:
                consecutive = 0
    return None

print(f"--- Square Border Analysis ---")
# Active row starts around 550
active_y = find_square_top(img, (100, 300), (550, 700))
print(f"Active square border top found at y={active_y}")

# Inactive row starts around 200
inactive_y = find_square_top(img, (100, 300), (200, 400))
print(f"Inactive square border top found at y={inactive_y}")
