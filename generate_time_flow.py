from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = "button_assets_sliced/time_flow"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WIDTH = 366
HEIGHT = 106
TEXT = "시작하기"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_SIZE = 40 # Smaller size requested

# Colors
BASE_COLOR = (0, 153, 83)    # The Green from Sample
OVERLAY_COLOR = (0, 100, 50, 180) # Darker green, semi-transparent?
# Or maybe the effect is "Light" fill on Dark background?
# User said "Show time flow ... like the first attached material".
# First material usually shows "Progress bar" style.
# Let's assume Dark Background (Unfilled) -> Bright Green (Filled) or vice versa.
# Given image 2 is "Start" green button, usually "Start" is the ACTIVE state.
# So maybe the button starts DARK/Empty and FILLS with this Green?
# Or starts with this Green and something else happens.
# "Time flow effect"
# Let's do: Base = Darker Green. Fill = The Sample Green (0, 153, 83).
# So it fills up to become the button in Image 2.

DARK_GREEN = (0, 100, 50)
FILL_COLOR = (0, 153, 83)
TEXT_COLOR = (255, 255, 255)

def create_frame(step_index, total_steps):
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Background (Unfilled Portion) -> Dark Green
    # Rounded Rect
    rect_bbox = [0, 0, WIDTH, HEIGHT]
    draw.rounded_rectangle(rect_bbox, radius=10, fill=DARK_GREEN)
    
    # 2. Fill (Progress) -> The Sample Green
    # Left to Right
    progress = step_index / (total_steps - 1) # 0.0 to 1.0
    if progress > 0:
        fill_width = int(WIDTH * progress)
        # Create a mask for rounded rect to clip the fill
        mask = Image.new('L', (WIDTH, HEIGHT), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(rect_bbox, radius=10, fill=255)
        
        # Create Fill Layer
        fill_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        fill_draw = ImageDraw.Draw(fill_layer)
        # Rect that is only 'fill_width' wide
        fill_draw.rectangle([0, 0, fill_width, HEIGHT], fill=FILL_COLOR)
        
        # Composite Fill masked by Rounded Rect
        img.paste(fill_layer, (0, 0), mask=mask)

    # 3. Text (Always on top)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=8) # Bold
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = (HEIGHT - text_h) // 2 - 5
    
    draw.text((text_x, text_y), TEXT, font=font, fill=TEXT_COLOR)
    
    return img

if __name__ == "__main__":
    TOTAL_STEPS = 6
    for i in range(TOTAL_STEPS):
        img = create_frame(i, TOTAL_STEPS) # 0 to 5
        # But for 10 "frames", maybe 1 is 10%, 10 is 100%?
        # Let's do 1 to 10 logic.
        # Step index i passed is 0-9.
        # My logic `progress = step_index / (TOTAL_STEPS-1)` makes 0->0%, 9->100%.
        # If user wants "Time Flow" maybe it starts empty?
        # Or Frame 1 is 10%?
        # Let's stick to 0-9 -> 0-100% just in case. 
        # Actually better: 1=10%, 10=100%. The "OFF" state is transparent.
        # The user overlays these.
        
        # Modified Logic:
        # Frame 1 should be 10% fill?
        # Frame 10 should be 100% fill.
        
        progress = (i + 1) / TOTAL_STEPS # 0.1 to 1.0
        
        # Redefine create_frame logic inside or verify loop passes correct index
        # Let's adjust main loop interactions.
        
        # Re-calc manually
        img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        rect_bbox = [0, 0, WIDTH, HEIGHT]
        
        # Mask for rounded corners
        mask = Image.new('L', (WIDTH, HEIGHT), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(rect_bbox, radius=10, fill=255)
        
        # Base: Dark Green (The "Previous/Empty" State)
        base = Image.new('RGBA', (WIDTH, HEIGHT), DARK_GREEN)
        
        # Fill: Light Green (The Target State)
        fill_w = int(WIDTH * progress)
        fill_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        fill_d = ImageDraw.Draw(fill_layer)
        fill_d.rectangle([0,0, fill_w, HEIGHT], fill=FILL_COLOR)
        
        base.paste(fill_layer, (0,0), mask=fill_layer) # No mask needed for rect paste? 
        # Wait, simply paste rect onto base.
        base.paste(fill_layer, (0,0)) 
        
        # Then Apply Rounded Mask to the whole thing
        final = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        final.paste(base, (0,0), mask=mask)
        
        # Text
        try:
             font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=8)
        except:
             font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), TEXT, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (WIDTH - text_w) // 2
        text_y = (HEIGHT - text_h) // 2 - 5
        
        text_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        text_d = ImageDraw.Draw(text_layer)
        text_d = ImageDraw.Draw(text_layer)
        # Stroke width simulates bold
        text_d.text((text_x, text_y), TEXT, font=font, fill=TEXT_COLOR, stroke_width=1, stroke_fill=TEXT_COLOR)
        
        final = Image.alpha_composite(final, text_layer)
        
        filename = f"time_flow_step_{i+1:02d}.png"
        path = os.path.join(OUTPUT_DIR, filename)
        final.save(path)
        print(f"Generated {path}")
