from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/ui design/icons/Buttons"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
# Size 40 for large buttons, might need adjustment for smaller ones. 
# I will use a default and allow override if needed, or dynamic scaling. 
# For consistency, let's target ~30-40 depending on button height.
DEFAULT_FONT_SIZE = 30

# Colors
COLOR_GREEN_ACTIVE = (0, 153, 83)    # Bright Green (Active)
COLOR_GREY_INACTIVE = (80, 80, 80)   # Dark Grey (Inactive)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_BORDER_ACTIVE = (255, 255, 255, 100) # Semi-transparent white

def create_button(filename_base, text, width, height, font_size=DEFAULT_FONT_SIZE, rounded_radius=15):
    """
    Generates two versions of the button: _active (Green) and _inactive (Grey).
    """
    states = [
        ("active", COLOR_GREEN_ACTIVE),
        ("inactive", COLOR_GREY_INACTIVE)
    ]
    
    try:
        font = ImageFont.truetype(FONT_PATH, font_size, index=8) # 8=Boldish
    except:
        font = ImageFont.load_default()

    for state_name, bg_color in states:
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Rounded Rectangle
        # drawn within 0,0 to width-1, height-1
        draw.rounded_rectangle((0, 0, width-1, height-1), radius=rounded_radius, fill=bg_color)
        
        # Border for Active state (Optional, but looks nice per reference "Glowing" feel)
        if state_name == "active":
             draw.rounded_rectangle((1, 1, width-2, height-2), radius=rounded_radius, outline=COLOR_BORDER_ACTIVE, width=2)
        
        # Text
        # textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (width - text_w) // 2
        y = (height - text_h) // 2 - 2 # slight offset
        
        draw.text((x, y), text, font=font, fill=COLOR_TEXT_WHITE)
        
        # Save
        full_filename = f"{filename_base}_{state_name}.png"
        save_path = os.path.join(OUTPUT_DIR, full_filename)
        img.save(save_path)
        print(f"Generated {full_filename}")

if __name__ == "__main__":
    print("Generating UI Buttons...")
    
    # Define Buttons: (FilenameBase, Text, Width, Height)
    # Sizes approximated from image relative to text
    
    # 1. Layout (Large)
    layout_buttons = [
        ("layout_full", "전체 화면", 220, 80),
        ("layout_split2", "2분할", 220, 80),
        ("layout_split3", "3분할", 220, 80),
        ("layout_split4", "4분할", 220, 80),
    ]
    
    # 2. Light / Power (Square-ish)
    power_buttons = [
        ("light_on", "켜기", 100, 80),
        ("light_off", "끄기", 100, 80),
    ]
    
    # 3. Black Screen (Large)
    misc_buttons = [
        ("black_screen", "BLACK\nSCREEN", 220, 80) # Multiline might need handling, but let's try standard
    ]
    
    # 4. LED Brightness (Slider style buttons)
    level_buttons = [
        ("level_low", "낮음", 80, 60),
        ("level_mid", "중간", 80, 60),
        ("level_high", "높음", 80, 60),
    ]
    
    # 5. Video Input (Wide)
    # [MODIFIED] Added explicit radius 20 for rounder look
    input_buttons = [
        ("src_pc1", "PC 1", 140, 70, 36, 20),
        ("src_pc2", "PC 2", 140, 70, 36, 20),
        ("src_cam1", "카메라 1", 140, 70, 36, 20),
        ("src_cam2", "카메라 2", 140, 70, 36, 20),
        ("src_wireless", "무선 입력", 140, 70, 36, 20),
        ("src_hdmi1", "HDMI 1", 140, 70, 36, 20),
        ("src_hdmi2", "HDMI 2", 140, 70, 36, 20),
    ]
    
    # 6. Video Output
    output_buttons = [
        ("out_proj", "프로젝터", 140, 70, 36, 20),
        ("out_mon1", "모니터 1", 140, 70, 36, 20),
        ("out_mon2", "모니터 2", 140, 70, 36, 20),
        ("out_cast", "방송 송출", 140, 70, 36, 20),
    ]
    
    # 7. Presets
    preset_buttons = [
        ("preset_1", "프리셋 1", 140, 70),
        ("preset_2", "프리셋 2", 140, 70),
        ("preset_3", "프리셋 3", 140, 70),
        ("preset_save", "저장", 100, 70),
        ("preset_load", "불러오기", 100, 70),
    ]
    
    # 8. Camera Control (Small Grid)
    cam_buttons = [
        ("cam_zoom_in", "줌+", 90, 70),
        ("cam_zoom_out", "줌-", 90, 70),
        ("cam_pan_up", "팬상", 90, 70),
        ("cam_pan_down", "팬하", 90, 70),
        ("cam_pan_left", "팬좌", 90, 70),
        ("cam_pan_right", "팬우", 90, 70),
        ("cam_tilt_up", "틸트 상", 90, 70),
        ("cam_tilt_down", "틸트 하", 90, 70),
        ("cam_focus_in", "포커스+", 90, 70),
        ("cam_focus_out", "포커스-", 90, 70),
    ]

    all_groups = [
        layout_buttons, power_buttons, misc_buttons, level_buttons, 
        input_buttons, output_buttons, preset_buttons, cam_buttons
    ]
    
    for group in all_groups:
        for item in group:
            if len(item) == 4:
                fname, txt, w, h = item
                create_button(fname, txt, w, h)
            elif len(item) == 5:
                fname, txt, w, h, fsize = item
                create_button(fname, txt, w, h, font_size=fsize)
            elif len(item) == 6:
                fname, txt, w, h, fsize, rad = item
                create_button(fname, txt, w, h, font_size=fsize, rounded_radius=rad)

    print("Done.")
