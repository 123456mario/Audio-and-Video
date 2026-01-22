import PIL.Image as Image
import sys

def analyze(path):
    img = Image.open(path).convert('RGBA')
    width, height = img.size
    # Get common colors
    colors = img.getcolors(width * height)
    sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
    
    print(f"File: {path}")
    print(f"Dimensions: {width}x{height}")
    print("Prominent Colors (RGBA):")
    for count, rgba in sorted_colors[:5]:
        print(f"  {rgba}: {count} pixels")

if __name__ == "__main__":
    analyze("/Users/gimdongseong/.gemini/antigravity/brain/7bafa0c9-9392-462c-9340-47ed3f07aa6a/uploaded_image_0_1766803216261.png")
    analyze("/Users/gimdongseong/.gemini/antigravity/brain/7bafa0c9-9392-462c-9340-47ed3f07aa6a/uploaded_image_1_1766803216261.png")
