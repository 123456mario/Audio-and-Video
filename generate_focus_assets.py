from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/button"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WIDTH = 366
HEIGHT = 106
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_SIZE = 40

# Colors
GREEN_ACTIVE = (0, 200, 0)    # Fluorescent Green (Matching other buttons)
GREEN_DIM = (0, 68, 34)       # Dark/Dim Green
TEXT_COLOR = (255, 255, 255)

def draw_button(filename, text, bg_color, text_opacity):
    # [MODIFIED] Use Transparent Background for Rounded Corners
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Draw Background with Rounded Corners
    draw.rounded_rectangle([0, 0, WIDTH-1, HEIGHT-1], radius=15, fill=bg_color)
    
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=8)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = (HEIGHT - text_h) // 2 - 5
    
    # Text Color with Opacity
    fill = list(TEXT_COLOR) + [int(255 * text_opacity)]
    
    # For dim state, maybe no stroke? 
    # Let's keep stroke consistent but faded
    stroke_fill = list(TEXT_COLOR) + [int(255 * text_opacity)]
    
    draw.text((text_x, text_y), text, font=font, fill=tuple(fill), stroke_width=1, stroke_fill=tuple(stroke_fill))
    
    # Add a border for Active state? 
    # CSS had a border. Let's add a subtle white inner border for Active to make it pop.
    if text_opacity > 0.8:
        draw.rounded_rectangle([0, 0, WIDTH-1, HEIGHT-1], radius=15, outline=(255,255,255, 50), width=2)

    save_path = os.path.join(OUTPUT_DIR, filename)
    img.save(save_path)
    print(f"Saved {save_path}")

if __name__ == "__main__":
    print("Generating Focus Shift Assets...")
    
    # 1. Top Button (Start)
    draw_button("top_active.png", "시작하기", GREEN_ACTIVE, 1.0)
    draw_button("top_dim.png", "시작하기", GREEN_DIM, 0.3)
    
    # 2. Bottom Button (Next Page)
    draw_button("bottom_active.png", "제어하기", GREEN_ACTIVE, 1.0)
    draw_button("bottom_dim.png", "제어하기", GREEN_DIM, 0.3)
    
    print("Done.")
