import os
from PIL import Image, ImageDraw

# Configuration
OUTPUT_DIR = "ui_assets/progress_bar"
WIDTH = 560
HEIGHT = 60
NUM_FRAMES = 21 # 0, 5, 10 ... 100
BG_COLOR = (230, 230, 230, 255) # Light Grey
FILL_COLOR = (0, 166, 81, 255) # Green (Brand Color)
BORDER_RADIUS = 10

def create_rounded_rect(draw, xy, cornerradius, fill, outline=None, width=1):
    upper_left, lower_right = xy
    draw.rounded_rectangle(xy, radius=cornerradius, fill=fill, outline=outline, width=width)

def generate_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Generating {NUM_FRAMES} progress bar images in {OUTPUT_DIR}...")

    for i in range(NUM_FRAMES):
        percent = i * (100 / (NUM_FRAMES - 1))
        filename = f"progress_{int(percent):03d}.png"
        path = os.path.join(OUTPUT_DIR, filename)

        # Create base image (Transparent)
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw Background (Track)
        create_rounded_rect(draw, [(0, 0), (WIDTH, HEIGHT)], BORDER_RADIUS, BG_COLOR)

        # Draw Progress (Fill)
        if percent > 0:
            fill_width = int((WIDTH * percent) / 100)
            # Ensure minimal width if visible matches radius to avoid artifacts, 
            # effectively masking it usually better but simple drawing works for flat UI
            if fill_width < BORDER_RADIUS * 2:
                # Handle small segments
                # For simplicity in this script, we draw a full rect but clipped? 
                # No, just draw logic:
                pass 
            
            # Draw the fill
            # To handle rounded corners correctly on the right side only when full, 
            # usually we draw a full rounded rect and crop, but standard drawing is easier.
            
            # Simple approach: Draw a rounded rect for the fill. 
            # If fill is partial, the right side should be flat? 
            # Or usually progress bars have rounded tips. Let's stick to rounded all around for "capsule" look.
            
            fill_box = [(0, 0), (fill_width, HEIGHT)]
            # If width is too small for radius, Pillow handles it or we clamp
            draw.rounded_rectangle([(0, 0), (max(fill_width, HEIGHT), HEIGHT)], radius=BORDER_RADIUS, fill=FILL_COLOR)
            
            # Hack: To make it look like a "fill" inside the track (not overflowing or weird shapes),
            # Ideally we paste the fill onto the bg.
            
            # Let's try a cleaner approach: Layer Compositing
            # 1. Background Layer
            bg_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
            bg_draw = ImageDraw.Draw(bg_layer)
            bg_draw.rounded_rectangle([(0,0), (WIDTH, HEIGHT)], radius=BORDER_RADIUS, fill=BG_COLOR)
            
            # 2. Fill Layer (Full Size Green)
            fill_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
            fill_draw = ImageDraw.Draw(fill_layer)
            fill_draw.rounded_rectangle([(0,0), (WIDTH, HEIGHT)], radius=BORDER_RADIUS, fill=FILL_COLOR)
            
            # 3. Mask (Rectangle of current progress width)
            mask = Image.new("L", (WIDTH, HEIGHT), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rectangle([(0,0), (fill_width, HEIGHT)], fill=255)
            
            # Composite: Paste Fill Layer onto BG Layer using Mask
            bg_layer.paste(fill_layer, (0,0), mask)
            img = bg_layer

        img.save(path)
        print(f"Saved {path}")

if __name__ == "__main__":
    try:
        generate_images()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
