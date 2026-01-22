from PIL import Image
import os

def get_y_sample_color(img_path):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    # Sample from the bottom right quadrant where the 'y' fill is likely to be
    # We'll look for non-white, non-transparent pixels in the right half
    sample_pixels = []
    for x in range(w // 2, w):
        for y in range(h // 2, h):
            pixel = img.getpixel((x, y))
            # Ignore transparent or purely white/black pixels if necessary
            if pixel[3] > 100: # Significant alpha
                # Look for green-ish pixels (high G, low R/B)
                r, g, b, a = pixel
                if g > r and g > b:
                    sample_pixels.append(pixel)
    
    if not sample_pixels:
        return None
    
    # Average the sampled pixels
    avg_r = sum(p[0] for p in sample_pixels) // len(sample_pixels)
    avg_g = sum(p[1] for p in sample_pixels) // len(sample_pixels)
    avg_b = sum(p[2] for p in sample_pixels) // len(sample_pixels)
    return (avg_r, avg_g, avg_b)

base_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인/text/ky_찬다"
ref_img = os.path.join(base_dir, "10.png")
test_img = os.path.join(base_dir, "1.png")

ref_color = get_y_sample_color(ref_img)
test_color = get_y_sample_color(test_img)

print(f"Reference (10.png) 'y' color: {ref_color}")
print(f"Test (1.png) 'y' color: {test_color}")
