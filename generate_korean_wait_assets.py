from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
TEXT_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/Text"
TEXT = "잠시만 기다려주세요.."
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

# Color constants
TEXT_COLOR_GREY = (0, 0, 0) # #888888

def ensure_dirs():
    if not os.path.exists(TEXT_DIR):
        os.makedirs(TEXT_DIR)

def generate_text_asset():
    # Match height 34, color #888888
    font_size = 20
    target_height = 34
    try:
        font = ImageFont.truetype(FONT_PATH, font_size, index=0)
    except:
        font = ImageFont.load_default()

    # Calculate width
    temp_img = Image.new('RGBA', (1000, 100), (0,0,0,0))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), TEXT, font=font)
    text_w = bbox[2] - bbox[0] + 10
    
    # Final image with fixed height 34
    img = Image.new('RGBA', (text_w, target_height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Center text vertically in 34px
    text_h = bbox[3] - bbox[1]
    y_pos = (target_height - text_h) // 2 - 2 
    
    draw.text((5, y_pos), TEXT, font=font, fill=TEXT_COLOR_GREY)
    
    # Save to local text dir
    save_path = os.path.join(TEXT_DIR, "wait_text_korean.png")
    img.save(save_path)
    
    # Save to the specific ui design/icons/Text folder
    final_dest = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/Text/wait_korean.png"
    img.save(final_dest)
    print(f"Saved {final_dest} ({text_w}x{target_height}) with color #888888")

if __name__ == "__main__":
    ensure_dirs()
    generate_text_asset()
