from PIL import Image, ImageDraw, ImageFont
import os
import math

# Configuration
OUTPUT_DIR = "button_assets_sliced/morph_transition"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WIDTH = 366
HEIGHT = 106
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_SIZE = 40

# Colors
GREEN_ACTIVE = (0, 153, 83)
GREEN_DARK = (0, 100, 50)
TEXT_COLOR = (255, 255, 255)

def draw_text(draw, text, opacity=255):
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=8)
    except:
        font = ImageFont.load_default()
    
    # Calculate position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = (HEIGHT - text_h) // 2 - 5
    
    fill = list(TEXT_COLOR) + [opacity]
    stroke_fill = list(TEXT_COLOR) + [opacity] # Simplified
    
    draw.text((text_x, text_y), text, font=font, fill=tuple(fill), stroke_width=1, stroke_fill=tuple(stroke_fill))

def create_top_frame(step, total_steps):
    """
    Top Button Animation:
    1. Shrink width significantly (Morph to blob)
    2. Move down towards bottom edge
    3. Fade text out early
    """
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Progress 0.0 to 1.0
    progress = step / (total_steps - 1)
    
    # Base State (Green Button)
    # Target State (Small Droplet at bottom center)
    
    # Width: 366 -> 40
    current_w = 366 - (366 - 40) * progress
    # Height: 106 -> 40
    current_h = 106 - (106 - 40) * progress
    
    # Center X
    cx = WIDTH // 2
    # Center Y: Starts at HEIGHT//2 (53). Moves down to HEIGHT (106)
    # Let's accelerate downwards
    cy = 53 + (HEIGHT - 53) * (progress * progress)
    
    # Bounding box for the shape
    x0 = cx - current_w // 2
    x1 = cx + current_w // 2
    y0 = cy - current_h // 2
    y1 = cy + current_h // 2
    
    # Draw Morphing Shape
    # Radius increases as it becomes smaller (rounder)
    # Initial radius 10. Final radius = width/2 = 20.
    radius = 10 + (10 * progress)
    
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=GREEN_ACTIVE)
    
    # Text Fade Out
    # Fades out quickly in first 30%
    text_opacity = max(0, 255 - int(255 * (progress * 3)))
    if text_opacity > 0:
        draw_text(draw, "시작하기", text_opacity)
        
    return img

def create_bottom_frame(step, total_steps):
    """
    Bottom Button Animation:
    1. Droplet enters from top
    2. Hits center
    3. Splashes/Expands to full rect
    4. Text pops in
    """
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    progress = step / (total_steps - 1)
    
    # Phase 1: Droplet Fall (0% - 30%)
    # Phase 2: Expansion (30% - 100%)
    
    if progress < 0.3:
        # Fall Phase
        local_p = progress / 0.3 # 0 to 1
        # Start: Top of frame (0). End: Center (53)
        cy = 0 + 53 * local_p
        
        # Shape: Small Droplet (40x40)
        w, h = 40, 40
        x0 = (WIDTH - w) // 2
        y0 = cy - h // 2
        draw.ellipse([x0, y0, x0+w, y0+h], fill=GREEN_ACTIVE)
        
    else:
        # Expansion Phase
        local_p = (progress - 0.3) / 0.7 # 0 to 1
        
        # Width: 40 -> 366
        w = 40 + (366 - 40) * local_p
        # Height: 40 -> 106
        h = 40 + (106 - 40) * local_p
        
        # Center stays at 53
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        x0 = cx - w // 2
        y0 = cy - h // 2
        
        # Radius: Starts at 20, ends at 10
        radius = 20 - (10 * local_p)
        
        draw.rounded_rectangle([x0, y0, x0+w, y0+h], radius=radius, fill=GREEN_ACTIVE)
        
        # Text Fade In (Late)
        # Starts appearing at 50% of total
        if progress > 0.5:
            text_p = (progress - 0.5) / 0.5
            opacity = int(255 * text_p)
            draw_text(draw, "다음 페이지 이동", opacity)

    return img

if __name__ == "__main__":
    # Settings
    # 6 frames for Top (Quick exit)
    # 8 frames for Bottom (Impact + Expand)
    
    print("Generating Morph Top...")
    for i in range(8):
        img = create_top_frame(i, 8)
        img.save(os.path.join(OUTPUT_DIR, f"morph_top_{i+1:02d}.png"))
        
    print("Generating Morph Bottom...")
    for i in range(8):
        img = create_bottom_frame(i, 8)
        img.save(os.path.join(OUTPUT_DIR, f"morph_bottom_{i+1:02d}.png"))
        
    print(f"Done. Check {OUTPUT_DIR}")
