from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/Text"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WIDTH = 366
HEIGHT = 106
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_SIZE = 40

# Colors
GREEN_ACTIVE = (0, 153, 83)   # Bright Green
GREEN_DIM = (0, 68, 34)       # Dark/Dim Green (Approx ~40% brightness of active)
TEXT_COLOR = (255, 255, 255)

def draw_button(filename, text, bg_color, text_opacity):
    img = Image.new('RGBA', (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
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
        draw.rectangle([0, 0, WIDTH-1, HEIGHT-1], outline=(255,255,255, 50), width=2)

    save_path = os.path.join(OUTPUT_DIR, filename)
    img.save(save_path)
    print(f"Saved {save_path}")

if __name__ == "__main__":
    print("Generating Focus Shift '제어하기' Assets...")
    
    # Generate Wait Button (Same style as Top/Bottom)
    draw_button("wait_active.png", "제어하기", GREEN_ACTIVE, 1.0)
    draw_button("wait_dim.png", "제어하기", GREEN_DIM, 0.3)
    
    print("Done.")
