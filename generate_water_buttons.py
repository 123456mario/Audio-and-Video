from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = "button_assets_sliced"  # Using the folder user mentioned
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WIDTH = 512
HEIGHT = 341
TEXT = "시작 하기"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_SIZE = 120

# Colors
BG_COLOR = (46, 125, 50)  # Dark Green (Approx #2E7D32)
TEXT_EMPTY_COLOR = (255, 255, 255, 30) # White with low opacity
TEXT_OUTLINE_COLOR = (200, 200, 200, 100)
WATER_COLOR = (33, 150, 243) # Blue #2196F3
TEXT_FILLED_COLOR = WATER_COLOR # Text becomes this color

def create_frame(step_index, total_steps):
    # create base
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw Rounded Rectangle Background
    # Using a slightly nicer green gradient if possible? Or solid.
    # User said "Green background". Let's stick to solid for Xilica consistency or matching btn_step_4.
    # btn_step_4 seemed to have a gradient. Let's do a vertical gradient?
    # For now, solid nice green.
    rect_bbox = [0, 0, WIDTH, HEIGHT]
    draw.rounded_rectangle(rect_bbox, radius=30, fill=BG_COLOR)
    
    # Load Font
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=0) # Index 0 usually Bold/Regular
        # Try finding Bold
        # For TTC/collections, indices vary. Usually 0=Regular, 1=Bold etc depending on font.
        # AppleSDGothicNeo: 0=Thin? 8=Bold? 
        # Let's try to list variation if possible, or just default.
        # Often index 8 or 9 is Bold. We'll stick to 0 properly or try another.
        # Actually let's assume 0 is readable.
    except:
        # Fallback
        font = ImageFont.load_default()
        print("Warning: Font not found, using default.")

    # Calculate Text Position
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = (HEIGHT - text_h) // 2 - 20 # Adjust slightly up

    # 1. Draw Empty Text (Base)
    draw.text((text_x, text_y), TEXT, font=font, fill=TEXT_EMPTY_COLOR, stroke_width=2, stroke_fill=TEXT_OUTLINE_COLOR)
    
    # 2. Draw Filled Text (Masked)
    # Create a separate image for text
    text_img = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((text_x, text_y), TEXT, font=font, fill=TEXT_FILLED_COLOR)
    
    # Create Mask for Progress
    # Left to Right fill
    progress = step_index / (total_steps - 1) # 0.0 to 1.0
    mask = Image.new('L', (WIDTH, HEIGHT), 0)
    mask_draw = ImageDraw.Draw(mask)
    
    fill_width = int(WIDTH * progress)
    mask_draw.rectangle([0, 0, fill_width, HEIGHT], fill=255)
    
    # Composite
    # Paste text_img onto img using mask
    img.paste(text_img, (0, 0), mask=match_text_mask(text_img, mask))
    
    return img

def match_text_mask(text_layer, progress_mask):
    # We want to show text_layer ONLY where progress_mask is White AND text_layer has alpha
    # Actually, img.paste(text_img, mask=mask) uses the mask's alpha.
    # If using 'mask' directly, it crops the whole image.
    # BUT we only want the TEXT to be cropped.
    # text_img has alpha for text shape.
    # progress_mask has alpha for progress.
    # Combine them: Final Mask = TextAlpha * ProgressAlpha
    
    r, g, b, a = text_layer.split()
    # 'a' is the text shape mask
    
    # Resize progress mask to match if needed (it is matched)
    
    # Combine
    # Since progress_mask is 'L', we can use ImageChops or Math
    from PIL import ImageChops
    combined_mask = ImageChops.multiply(a, progress_mask)
    return combined_mask

if __name__ == "__main__":
    TOTAL_STEPS = 10
    for i in range(TOTAL_STEPS):
        # Step 1 to 10
        img = create_frame(i, TOTAL_STEPS) # 0 to 9 logic? 
        # If user wants 10 frames 0-100%, let's do 0, 11, 22... OR 1 to 10.
        # Let's map 0 -> 0%, 9 -> 100%.
        
        filename = f"water_fill_step_{i+1:02d}.png"
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path)
        print(f"Generated {path}")

