import os
from PIL import Image

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
mute_img_path = os.path.join(brain_dir, "flat_mute_active_red_1767929422887.png")
sound_img_path = os.path.join(brain_dir, "flat_mute_inactive_white_1767929436729.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def process_and_resize(img_path, output_name, target_size=(90, 70)):
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # 1. Auto-crop black background
        gray = img.convert("L")
        threshold = 20
        mask = gray.point(lambda p: 255 if p > threshold else 0)
        bbox = mask.getbbox()
        
        if bbox:
            img_cropped = img.crop(bbox)
        else:
            print(f"Warning: Could not detect button in {img_path}")
            img_cropped = img

        # 2. Resize to specific target size (Width, Height)
        # Note: This will stretch the square icon to rectangle.
        # Use high quality downsampling
        img_resized = img_cropped.resize(target_size, Image.Resampling.LANCZOS)

        # Save
        output_path = os.path.join(output_dir, output_name)
        img_resized.save(output_path)
        print(f"Saved {output_path} ({target_size[0]}x{target_size[1]})")
        
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

# Process Mute (Red) -> 90x70
process_and_resize(mute_img_path, "btn_mute_active.png", target_size=(90, 70))

# Process Sound (White) -> 90x70
process_and_resize(sound_img_path, "btn_mute_inactive.png", target_size=(90, 70))
