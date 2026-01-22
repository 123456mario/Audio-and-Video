import os
from PIL import Image, ImageEnhance

# Configuration
base_file = "/Users/gimdongseong/.gemini/antigravity/brain/7d881365-0c82-4ae7-965e-eaeafa58df40/uploaded_image_1765867901428.png"
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/button_assets_wiped"
os.makedirs(output_dir, exist_ok=True)

def create_wipe_sequence():
    try:
        # Load original (The "Full" state)
        img_full = Image.open(base_file).convert("RGBA")
        width, height = img_full.size
        
        # Create "Empty" state (Dimmed)
        # Reduce brightness to 30% or make it semi-transparent?
        # Let's reduce brightness to look "inactive"
        enhancer = ImageEnhance.Brightness(img_full)
        img_empty = enhancer.enhance(0.4) # 40% brightness
        # Also maybe desaturate slightly?
        converter = ImageEnhance.Color(img_empty)
        img_empty = converter.enhance(0.5) # 50% saturation
        
        # Generate 31 frames (0 to 30)
        # 0 = 0% filled
        # 30 = 100% filled
        total_frames = 31
        
        for i in range(total_frames):
            # Calculate fill width
            if i == 0:
                fill_w = 0
            else:
                fill_w = int((i / (total_frames - 1)) * width)
            
            # Create frame canvas (starting with Empty)
            frame = img_empty.copy()
            
            # Paste the Full version cropped to fill_w
            if fill_w > 0:
                crop_full = img_full.crop((0, 0, fill_w, height))
                frame.paste(crop_full, (0, 0))
            
            # Save
            filename = f"btn_step_{i:02d}.png"
            out_path = os.path.join(output_dir, filename)
            frame.save(out_path)
            print(f"Saved: {out_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_wipe_sequence()
