import os
from PIL import Image

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
mute_img_path = os.path.join(brain_dir, "button_mute_on_red_1767929326389.png")
sound_img_path = os.path.join(brain_dir, "button_sound_on_white_1767929343824.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def process_button(img_path, output_name):
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # 1. Auto-crop black background
        gray = img.convert("L")
        threshold = 20
        mask = gray.point(lambda p: 255 if p > threshold else 0)
        bbox = mask.getbbox()
        
        if bbox:
            # Crop to content
            left, upper, right, lower = bbox
            width = right - left
            height = lower - upper
            
            # Simple tight crop then resize
            img_cropped = img.crop(bbox)
            
            # Resize to 100x100
            img_resized = img_cropped.resize((100, 100), Image.Resampling.LANCZOS)
            
        else:
            print(f"Warning: Could not detect button in {img_path}")
            img_resized = img.resize((100, 100), Image.Resampling.LANCZOS)

        # Save
        text_path = os.path.join(output_dir, output_name)
        img_resized.save(text_path)
        print(f"Saved {text_path}")
        
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

# Process Mute (Red) is Mute ON (Silence)
process_button(mute_img_path, "btn_mute_active.png")

# Process Sound (White) is Mute OFF (Sound)
process_button(sound_img_path, "btn_mute_inactive.png")
