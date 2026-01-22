import PIL.Image as Image
import os

def create_icons():
    # Source: uploaded_image_1 (Green Button)
    src_on = "/Users/gimdongseong/.gemini/antigravity/brain/7bafa0c9-9392-462c-9340-47ed3f07aa6a/uploaded_image_1_1766803216261.png"
    target_dir = "/Users/gimdongseong/Documents/GitHub/behringer-mixer/icons"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 1. Segment On (Green)
    img_on = Image.open(src_on).convert('RGBA')
    img_on.save(os.path.join(target_dir, "segment_on.png"), "PNG")
    print(f"Updated segment_on.png: {img_on.size}")

    # 2. Segment Off (Transparent)
    # Important: Must match size of segment_on for toggle consistency
    img_off = Image.new('RGBA', img_on.size, (0, 0, 0, 0))
    img_off.save(os.path.join(target_dir, "segment_off.png"), "PNG")
    print(f"Updated segment_off.png: {img_off.size}")

if __name__ == "__main__":
    create_icons()
