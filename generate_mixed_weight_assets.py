from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
DEST_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/Text"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
REG_INDEX = 0
BOLD_INDEX = 6
TEXT_COLOR_GREY = (136, 136, 136)
TEXT_COLOR_BLACK = (0, 0, 0)
TARGET_HEIGHT = 34
FONT_SIZE = 22

def ensure_dirs():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

def generate_mixed_asset(parts, filename):
    """
    parts: list of tuples (text, is_bold, color)
    """
    try:
        font_reg = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=REG_INDEX)
        font_bold = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=BOLD_INDEX)
    except:
        font_reg = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    # Calculate total width
    total_w = 0
    temp_img = Image.new('RGBA', (2000, 100), (0,0,0,0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    measurements = []
    for text, is_bold, color in parts:
        f = font_bold if is_bold else font_reg
        bbox = temp_draw.textbbox((0, 0), text, font=f)
        w = bbox[2] - bbox[0]
        measurements.append((text, f, w, bbox, color))
        total_w += w
    
    total_w += 20 # Padding

    # Final image
    img = Image.new('RGBA', (total_w, TARGET_HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    current_x = 10
    for text, f, w, bbox, color in measurements:
        text_h = bbox[3] - bbox[1]
        y_pos = (TARGET_HEIGHT - text_h) // 2 - 2
        draw.text((current_x, y_pos), text, font=f, fill=color)
        current_x += w
    
    save_path = os.path.join(DEST_DIR, filename)
    img.save(save_path)
    print(f"✅ Generated {filename} ({total_w}x{TARGET_HEIGHT}) at {save_path}")

if __name__ == "__main__":
    ensure_dirs()
    
    # 1. 안내문구 1
    # Regular: Grey, [Bold]: Black
    parts1 = [
        ("시스템을 시작하려면", False, TEXT_COLOR_GREY),
        ("[시작하기]", True, TEXT_COLOR_BLACK),
        (" 버튼을 눌러주세요", False, TEXT_COLOR_GREY)
    ]
    generate_mixed_asset(parts1, "guidance_start_hybrid2.png")
    
    # 2. 안내문구 2
    parts2 = [
        ("시스템준비가 완료되면 ", False, TEXT_COLOR_GREY),
        ("[제어하기]", True, TEXT_COLOR_BLACK),
        (" 버튼을 눌러주세요", False, TEXT_COLOR_GREY)
    ]
    generate_mixed_asset(parts2, "guidance_controlpage_hybrid2.png")
