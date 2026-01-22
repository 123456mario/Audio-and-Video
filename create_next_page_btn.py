import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Paths
output_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/아이콘"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
# Constants from "Start" button analysis
WIDTH = 352
HEIGHT = 96
# Updated Color from User Uploaded Reference (Vibrant Green)
BG_COLOR = (20, 160, 96, 255) 
TEXT_COLOR = (255, 255, 255, 255)
TEXT = "다음페이지"

# Font - AppleGothic for Korean
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

def create_btn():
    try:
        # Fix Black Border Issue by using Transparent Green background
        # (R, G, B, 0) instead of (0, 0, 0, 0)
        bg_transparent = BG_COLOR[:3] + (0,)
        img = Image.new("RGBA", (WIDTH, HEIGHT), bg_transparent)
        draw = ImageDraw.Draw(img)
        
        # Draw Rounded Rect
        # Corner radius looks standard, maybe 16 or 20? Let's guess 20 based on height 96
        draw.rounded_rectangle((0, 0, WIDTH, HEIGHT), radius=20, fill=BG_COLOR)
        
        # Load Font
        try:
             # Height 96 -> Text size around 40-48?
             font = ImageFont.truetype(font_path, 40)
        except:
             print("Font not found, using default.")
             font = ImageFont.load_default()
             
        # Center Text
        bbox = draw.textbbox((0, 0), TEXT, font=font)
        w_text = bbox[2] - bbox[0]
        h_text = bbox[3] - bbox[1]
        
        x = (WIDTH - w_text) // 2
        y = (HEIGHT - h_text) // 2 - 5 # Slight visual adjustment
        
        draw.text((x, y), TEXT, font=font, fill=TEXT_COLOR)
        
        # Save
        filename = "btn_next_page.png"
        path = os.path.join(output_dir, filename)
        img.save(path)
        print(f"Saved: {path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

create_btn()
