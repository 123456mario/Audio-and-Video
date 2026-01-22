
from PIL import Image, ImageDraw, ImageFilter

def create_button(filename, color_start, color_end, glow_color, is_lit):
    size = (100, 100)
    # Create valid image with alpha channel
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dimensions for the button face
    padding = 10
    x0, y0 = padding, padding
    x1, y1 = size[0] - padding, size[1] - padding
    radius = 15
    
    # 1. Glow / Shadow (Outer)
    if is_lit:
        # Create a glow layer
        glow_layer = Image.new('RGBA', size, (0,0,0,0))
        gw_draw = ImageDraw.Draw(glow_layer)
        # Draw a slightly larger rect for glow
        gw_draw.rounded_rectangle([x0-2, y0-2, x1+2, y1+2], radius=radius, fill=glow_color)
        # Blur it
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(5))
        img = Image.alpha_composite(glow_layer, img)
        draw = ImageDraw.Draw(img) # Update draw object
    
    # 2. Button Body (Gradient Simulation)
    # We'll just draw concentrated concentric rounded rects to simulate a gradient/dome
    center_x, center_y = 50, 50
    max_dist = 40
    
    for i in range(40):
        # Interpolate color
        ratio = i / 40.0
        # For a "dome" look, lighter in center
        r = int(color_start[0] * (1-ratio) + color_end[0] * ratio)
        g = int(color_start[1] * (1-ratio) + color_end[1] * ratio)
        b = int(color_start[2] * (1-ratio) + color_end[2] * ratio)
        a = 255
        
        inset = i
        if x0+inset < x1-inset:
             draw.rounded_rectangle([x0+inset, y0+inset, x1-inset, y1-inset], radius=max(1, radius-inset), outline=None, fill=(r,g,b,a))

    # 3. Glossy Highlight (Top reflection)
    # White semi-transparent oval on top half
    draw.ellipse([x0+10, y0+5, x1-10, y0+40], fill=(255, 255, 255, 60))
    
    # 4. Border/Rim
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=(200, 200, 200, 150), width=2)

    img.save(filename)
    print(f"Generated {filename}")

# Colors (RGB)
# OFF: White/Grey look
off_center = (240, 240, 240)
off_edge = (150, 150, 150)
off_glow = (0, 0, 0, 0) # No glow

# ON: Bright Green look (Fluorescent)
on_center = (200, 255, 200) # Almost white-green center
on_edge = (0, 200, 0)       # Green edge
on_glow = (0, 255, 0, 100)  # Green glow opacity

create_button("button_off_white.png", off_center, off_edge, off_glow, False)
create_button("button_on_green.png", on_center, on_edge, on_glow, True)
