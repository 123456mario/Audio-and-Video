import os
from PIL import Image

# Directories
src_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui_design_assets"
dest_dir = os.path.join(src_dir, "sliced")
os.makedirs(dest_dir, exist_ok=True)

def slice_image(image_path, cuts, prefix):
    img = Image.open(image_path)
    for l, t, r, b, name in cuts:
        cropped = img.crop((l, t, r, b))
        out_name = f"{prefix}_{name}.png"
        cropped.save(os.path.join(dest_dir, out_name))
        print(f"Saved: {out_name} | Size: {cropped.size}")

# ULTRA PRECISION - Moving away from any possible text labels
# Inactive Icon top confirmed at y=293. Active Icon top confirmed at y=621.
# We use +5 pixels to be safe.
ptz_cuts = [
    # Inactive - Top: 300, Bottom: 480
    (96, 300, 290, 480, "up_inactive"),
    (309, 300, 500, 480, "down_inactive"),
    (523, 300, 715, 480, "left_inactive"),
    (735, 300, 930, 480, "right_inactive"),
    # Active - Top: 625, Bottom: 820
    (92, 625, 295, 820, "up_active"),
    (305, 625, 505, 820, "down_active"),
    (518, 625, 718, 820, "left_active"),
    (732, 625, 935, 820, "right_active"),
]
slice_image(os.path.join(src_dir, "arrow_buttons_white_green_1765834662501.png"), ptz_cuts, "ptz")

# Zoom
zoom_cuts = [
    (245, 280, 495, 510, "in_inactive"),
    (525, 280, 775, 510, "out_inactive"),
    (245, 620, 495, 850, "in_active"),
    (525, 620, 775, 850, "out_active"),
]
slice_image(os.path.join(src_dir, "zoom_buttons_white_green_1765834693420.png"), zoom_cuts, "zoom")

# CAM Front
cam_front_cuts = [
    (200, 310, 825, 440, "front_inactive"),
    (200, 640, 825, 770, "front_active"),
]
slice_image(os.path.join(src_dir, "cam_front_buttons_white_green_1765834500487.png"), cam_front_cuts, "cam")

# CAM Side
cam_side_cuts = [
    (165, 290, 860, 460, "side_inactive"),
    (165, 640, 860, 811, "side_active"),
]
slice_image(os.path.join(src_dir, "cam_side_buttons_white_green_1765834532463.png"), cam_side_cuts, "cam")

print("\nUltra-Precision slicing complete.")
