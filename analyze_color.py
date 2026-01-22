from PIL import Image
import os

# Path to the 2nd image (Color/Size reference)
# Note: The tool output gave the path /Users/gimdongseong/.gemini/antigravity/brain/68d1c8d1-3ede-4b97-8e56-d4d3173347ad/uploaded_image_1_1766274148626.png
# I need to find where it is or use the path provided in metadata.
# The metadata said: /Users/gimdongseong/.gemini/antigravity/brain/68d1c8d1-3ede-4b97-8e56-d4d3173347ad/uploaded_image_1_1766274148626.png
# I will use that absolute path.

img_path = "/Users/gimdongseong/.gemini/antigravity/brain/68d1c8d1-3ede-4b97-8e56-d4d3173347ad/uploaded_image_1_1766274148626.png"

try:
    img = Image.open(img_path)
    print(f"Size: {img.size}")
    
    # Get dominant color or center color
    # Center pixel
    cx, cy = img.size[0] // 2, img.size[1] // 2
    center_pixel = img.getpixel((cx, cy))
    print(f"Center Pixel: {center_pixel}")
    
    # Get a pixel from top left corner (background?)
    sample_pixel = img.getpixel((10, 10))
    print(f"Sample Pixel (10,10): {sample_pixel}")

except Exception as e:
    print(f"Error: {e}")
