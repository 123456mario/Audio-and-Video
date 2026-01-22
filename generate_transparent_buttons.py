from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def create_button(text, color, filename, width=200, height=80, radius=20):
    # Create a transparent image
    # Increased size for shadow/glow if needed, but keeping it simple for now
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define bounding box
    # Inset slightly to avoid anti-aliasing clipping
    bbox = [2, 2, width-2, height-2]
    
    # Draw rounded rectangle
    # Outline
    draw.rounded_rectangle(bbox, radius=radius, fill=color, outline=(255, 255, 255, 100), width=2)

    # Add Text
    try:
        # Try to use a system font, fallback to default
        font_path = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(font_path):
             font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        
        font = ImageFont.truetype(font_path, 32)
    except:
        font = ImageFont.load_default()

    # Calculate text position (centered)
    # Using getbbox for newer Pillow versions
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    x = (width - text_w) / 2
    y = (height - text_h) / 2 - 4 # slight vertical adjustment

    # Draw Text Shadow
    draw.text((x+1, y+1), text, font=font, fill=(0, 0, 0, 128))
    # Draw Text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    # Save
    img.save(filename)
    print(f"Generated {filename}")

# Colors
# Power On: Greenish
# Power Off: Reddish or Dark Grey? Usually Power Off is Red or Grey.
# Let's verify standard UI. "Power Off" -> Red. "Power On" -> Green.

create_button("POWER ON", (40, 180, 40, 255), "sys_power_on.png")
create_button("POWER OFF", (200, 50, 50, 255), "sys_power_off.png")
