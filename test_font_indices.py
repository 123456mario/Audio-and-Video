from PIL import Image, ImageDraw, ImageFont
import os

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
TEXT = "시작하기 [다음 페이지]"
OUTPUT_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/font_test"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for i in range(10):
    try:
        font = ImageFont.truetype(FONT_PATH, 22, index=i)
        img = Image.new('RGBA', (400, 50), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"Index {i}: {TEXT}", font=font, fill=(0, 0, 0))
        img.save(os.path.join(OUTPUT_DIR, f"font_index_{i}.png"))
        print(f"Saved index {i}")
    except Exception as e:
        print(f"Error at index {i}: {e}")
