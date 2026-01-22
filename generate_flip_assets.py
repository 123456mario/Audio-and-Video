from PIL import Image, ImageDraw, ImageFont, ImageTransform
import os
import math

# Configuration
OUTPUT_DIR = "button_assets_sliced/flip_transition"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WIDTH = 366
HEIGHT = 106
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_SIZE = 40

# Colors
BASE_GREEN = (0, 100, 50)     # Darker Base
ACTIVE_GREEN = (0, 153, 83)   # Lighter Active
TEXT_COLOR = (255, 255, 255)

def apply_perspective_transform(img, angle):
    """
    Simulate rotating a rectangle around its X-axis (vertical flip).
    angle: 0 to 90 degrees.
    Returns: a new Image object with transparency.
    """
    w, h = img.size
    
    # Simple compression for 90 degrees rotation simulation
    # Height scales by cos(angle)
    rad = math.radians(angle)
    scale_y = math.cos(rad)
    new_h = int(h * scale_y)
    
    if new_h < 1:
        new_h = 1 # Avoid zero height
        
    # Resize vertically to simulate "flat" rotation
    resized = img.resize((w, new_h), Image.Resampling.LANCZOS)
    
    # Apply Shading (Darken as it turns away)
    # 0 degrees = 0% black (Original brightness)
    # 90 degrees = 60% black (Shadow)
    shade_opacity = int(150 * (angle / 90.0)) # Max 150/255 opacity
    
    if shade_opacity > 0:
        shade_layer = Image.new('RGBA', resized.size, (0, 0, 0, shade_opacity))
        # Mask shade to the button shape (alpha channel)
        resized = Image.alpha_composite(resized, shade_layer)
    
    # Create canvas of original size to center it
    final = Image.new('RGBA', (w, h), (0,0,0,0))
    y_offset = (h - new_h) // 2
    final.paste(resized, (0, y_offset))
    
    return final

def create_base_button(text, bg_color):
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
    
    # Rounded Rect Mask
    mask = Image.new('L', (WIDTH, HEIGHT), 0)
    d_mask = ImageDraw.Draw(mask)
    d_mask.rounded_rectangle([0,0, WIDTH, HEIGHT], radius=10, fill=255)
    
    # Colored Rect
    color_layer = Image.new('RGBA', (WIDTH, HEIGHT), bg_color)
    img.paste(color_layer, (0,0), mask=mask)
    
    # Text
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=8)
    except:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = (HEIGHT - text_h) // 2 - 5
    
    # Stroke text
    draw.text((text_x, text_y), text, font=font, fill=TEXT_COLOR, stroke_width=1, stroke_fill=TEXT_COLOR)
    
    return img

if __name__ == "__main__":
    TOTAL_STEPS = 6
    
    # PART 1: TOP BUTTON (START) -> FLIP OUT (0 to 90 degrees)
    # Text: 시작하기
    # Color: Start as ACTIVE_GREEN (Full), end as invisible
    base_top = create_base_button("시작하기", ACTIVE_GREEN)
    
    print("Generating Top Button Flip-Out sequence...")
    for i in range(TOTAL_STEPS):
        # Progress 0.0 to 1.0
        progress = i / (TOTAL_STEPS - 1)
        angle = 90 * progress # 0 -> 90
        
        frame = apply_perspective_transform(base_top, angle)
        
        filename = f"flip_top_{i+1:02d}.png"
        frame.save(os.path.join(OUTPUT_DIR, filename))
        print(f"Saved {filename}")

    # PART 2: BOTTOM BUTTON (NEXT) -> FLIP IN (-90 to 0 degrees, or 90 to 0)
    # Text: 다음 페이지 이동
    # Color: ACTIVE_GREEN
    base_bottom = create_base_button("다음 페이지 이동", ACTIVE_GREEN)
    
    print("Generating Bottom Button Flip-In sequence...")
    for i in range(TOTAL_STEPS):
        # Progress 0.0 to 1.0
        progress = i / (TOTAL_STEPS - 1)
        
        # We want to go from 90 (invisible) to 0 (visible)
        # But logically 'Flip In' usually starts at 90.
        angle = 90 * (1.0 - progress) # 90 -> 0
        
        frame = apply_perspective_transform(base_bottom, angle)
        
        filename = f"flip_bottom_{i+1:02d}.png"
        frame.save(os.path.join(OUTPUT_DIR, filename))
        print(f"Saved {filename}")
