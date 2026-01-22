import os
from PIL import Image, ImageDraw, ImageOps

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
icon_speaker_path = os.path.join(brain_dir, "icon_speaker_black_1767929835911.png")
icon_mute_path = os.path.join(brain_dir, "icon_mute_black_1767929852783.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_button(icon_path, bg_color, output_name, invert_icon=False, icon_scale=0.6):
    try:
        # Load Icon
        icon_img = Image.open(icon_path).convert("RGBA")
        
        # 1. Clean up icon: Crop to content
        gray = icon_img.convert("L")
        # Invert if white background: White(255) -> Black(0). Then threshold.
        # Assuming the generated images are Black Icon on White Background.
        # We want the Black parts.
        # So we inverse: White(255)->0, Black(0)->255.
        inverted_gray = ImageOps.invert(gray.convert("RGB")).convert("L") # Invert needs RGB or L
        
        # Threshold to get mask of valid pixels
        threshold = 50
        mask = inverted_gray.point(lambda p: 255 if p > threshold else 0)
        bbox = mask.getbbox()
        
        if bbox:
            icon_cropped = icon_img.crop(bbox)
        else:
            print(f"Warning: Could not detect icon in {icon_path}")
            icon_cropped = icon_img

        # 2. Resize Icon to fit nicely in 90x70
        # Let's say max height is 40px (since button is 70px)
        button_w, button_h = 90, 70
        target_h = int(button_h * icon_scale) # e.g. 70 * 0.6 = 42
        
        # Calculate aspect ratio
        w, h = icon_cropped.size
        ratio = w / h
        target_w = int(target_h * ratio)
        
        # If target_w > button_w (unlikely for speaker icon), cap it
        if target_w > button_w * 0.8:
             target_w = int(button_w * 0.8)
             target_h = int(target_w / ratio)
             
        icon_resized = icon_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 3. Create Button Background
        # Create transparent base
        button = Image.new("RGBA", (button_w, button_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(button)
        
        # Draw rounded rectangle
        # Corner radius
        radius = 15
        draw.rounded_rectangle((0, 0, button_w, button_h), radius=radius, fill=bg_color)
        
        # 4. Prepare Icon Overlay
        # If we need to change icon color (e.g. make it White or Black), we can use the mask
        # Extracted mask from resized icon (alpha channel or luminosity)
        
        # For the provided images (Black icon on white):
        # We want the Black part to become the Icon Color.
        # The White part should be Transparent.
        
        # Let's create a solid color image for the icon and use the resized icon as masking source
        # But first we need a good alpha mask of the icon.
        # From the cropped icon:
        # Convert to grayscale
        icon_gray = icon_resized.convert("L")
        # Invert so black (icon) becomes white (opacity)
        icon_alpha = ImageOps.invert(icon_gray)
        # Threshold to clean up edges? optional
        
        # Color to fill icon with
        # If invert_icon=True (Mute button), we want White Icon.
        # If False (Sound button), we want Black Icon.
        icon_fill_color = (255, 255, 255, 255) if invert_icon else (0, 0, 0, 255)
        
        colored_icon = Image.new("RGBA", (target_w, target_h), icon_fill_color)
        colored_icon.putalpha(icon_alpha)
        
        # 5. Paste Icon Centered
        pos_x = (button_w - target_w) // 2
        pos_y = (button_h - target_h) // 2
        
        # Composite
        button.alpha_composite(colored_icon, (pos_x, pos_y))
        
        # Save
        output_path = os.path.join(output_dir, output_name)
        button.save(output_path)
        print(f"Saved {output_path}")

    except Exception as e:
        print(f"Error processing {icon_path}: {e}")

# Process Mute Active (Red BG, White Icon)
# Color: Deep Red #CC0000 -> (204, 0, 0)
create_button(icon_mute_path, (204, 0, 0, 255), "btn_mute_active.png", invert_icon=True, icon_scale=0.55)

# Process Sound Inactive (White BG, Black Icon)
# Color: Light Grey/White #F0F0F0 -> (240, 240, 240)
create_button(icon_speaker_path, (240, 240, 240, 255), "btn_mute_inactive.png", invert_icon=False, icon_scale=0.55)
