import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Paths
brain_dir = "/Users/gimdongseong/.gemini/antigravity/brain/067fcfb4-5cf8-4bf6-bcda-89d1c2a4f10f"
green_img_path = os.path.join(brain_dir, "button_concept_green_1767929037111.png")
white_img_path = os.path.join(brain_dir, "button_concept_white_1767929055122.png")
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def process_button(img_path, text, output_name_base, text_color=(0, 0, 0)):
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # 1. Auto-crop black background
        # Convert to grayscale to find bounding box
        gray = img.convert("L")
        # Threshold: anything brighter than very dark gray is kept
        threshold = 20
        # Create a mask where brighter pixels are white, background is black
        mask = gray.point(lambda p: 255 if p > threshold else 0)
        bbox = mask.getbbox()
        
        if bbox:
            # Crop to content
            left, upper, right, lower = bbox
            width = right - left
            height = lower - upper
            
            # Make the crop square to avoid distortion if possible, or just crop tight
            # The generated buttons are square, so tight crop should be roughly square.
            # But let's force a square crop around the center to be safe.
            cx = (left + right) // 2
            cy = (upper + lower) // 2
            size = max(width, height)
            
            # We want the crop to be exactly 'size' x 'size' centered
            # Ensure we don't go out of image bounds
            half = size // 2
            
            # Simple tight crop is safer usually, then resize.
            # But resizing a rectangle to square distorts it.
            # Let's crop tight first.
            img_cropped = img.crop(bbox)
            
            # If not square, pad or crop?
            # They should be square. If 5% difference, just resize.
            # If huge difference, we have a problem.
            # Assuming square.
            
            img_resized = img_cropped.resize((100, 100), Image.Resampling.LANCZOS)
            
        else:
            print(f"Warning: Could not detect button in {img_path}")
            img_resized = img.resize((100, 100), Image.Resampling.LANCZOS)

        # Save blank version
        blank_path = os.path.join(output_dir, f"{output_name_base}_blank.png")
        img_resized.save(blank_path)
        print(f"Saved {blank_path}")

        # Add Text
        # Try to load a nice font
        font_path = "/System/Library/Fonts/Helvetica.ttc"
        try:
            # Use a slightly bigger weight if possible, or just regular
            font = ImageFont.truetype(font_path, 30) 
        except:
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img_resized)
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        x = (100 - text_w) / 2
        y = (100 - text_h) / 2 - 3 # Optical center adjustment
        
        # Draw text
        draw.text((x, y), text, font=font, fill=text_color)
        
        text_path = os.path.join(output_dir, f"{output_name_base}_text.png")
        img_resized.save(text_path)
        print(f"Saved {text_path}")
        
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

# Process Green (ON)
process_button(green_img_path, "ON", "btn_on", text_color=(0, 0, 0))

# Process White (OFF)
process_button(white_img_path, "OFF", "btn_off", text_color=(0, 0, 0))
