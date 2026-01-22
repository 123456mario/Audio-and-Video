from PIL import Image
import sys

def colorize_icon(input_path, output_path, color_rgb):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # item is (r, g, b, a)
            avg = (item[0] + item[1] + item[2]) / 3
            
            # Previous Logic (Standard Black on White):
            # avg < 200 (Dark) -> Color
            # avg >= 200 (Light) -> Transparent
            
            # User says it was swapped. So the image might be White on Black.
            # OR they want the 'Light' part to be the icon.
            
            # NEW LOGIC: Inverted.
            # avg < 200 (Dark) -> Transparent (Background)
            # avg >= 200 (Light) -> Color (Icon)
            
            if avg < 100: # Dark -> Background -> Transparent
                newData.append((0, 0, 0, 0))
            else:
                # Light -> Icon -> Target Color
                newData.append((color_rgb[0], color_rgb[1], color_rgb[2], 255))
        
        img.putdata(newData)
        img.save(output_path, "PNG")
        print(f"Colorized (Inverted Logic) {output_path} with {color_rgb}")
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

input_file = "/Users/gimdongseong/.gemini/antigravity/brain/9990c611-1659-4f0c-8b74-8a2745ea4a8a/uploaded_image_1768008948993.png"

# Power On: Green
colorize_icon(input_file, "아이콘/sys_power_on.png", (0, 255, 0))

# Power Off: White
colorize_icon(input_file, "아이콘/sys_power_off.png", (255, 255, 255))
