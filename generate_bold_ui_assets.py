from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
TEXT_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
BOLD_INDEX = 4 # Common index for Bold in AppleSDGothicNeo
TEXT_COLOR_GREY = (136, 136, 136) # #888888
TARGET_HEIGHT = 34

def ensure_dirs():
    if not os.path.exists(TEXT_DIR):
        os.makedirs(TEXT_DIR)

def generate_bold_asset(text, filename):
    font_size = 22
    try:
        font = ImageFont.truetype(FONT_PATH, font_size, index=BOLD_INDEX)
    except:
        font = ImageFont.load_default()

    # Calculate width
    temp_img = Image.new('RGBA', (2000, 100), (0,0,0,0))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0] + 10
    
    # Final image with fixed height 34
    img = Image.new('RGBA', (text_w, TARGET_HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Center text vertically
    text_h = bbox[3] - bbox[1]
    y_pos = (TARGET_HEIGHT - text_h) // 2 - 2 
    
    draw.text((5, y_pos), text, font=font, fill=TEXT_COLOR_GREY)
    
    save_path = os.path.join(TEXT_DIR, filename)
    img.save(save_path)
    print(f"✅ Generated {filename} ({text_w}x{TARGET_HEIGHT})")

if __name__ == "__main__":
    ensure_dirs()
    generate_bold_asset("다음 페이지", "next_page_bold.png")
    generate_bold_asset("제어를 시작하려면 [시작하기] 버튼을 눌러주세요", "start_guidance_bold.png")
