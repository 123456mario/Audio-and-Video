from PIL import Image
import sys

def remove_black_background(input_path, output_path, tolerance=30):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # Check if pixel is black-ish
            if item[0] < tolerance and item[1] < tolerance and item[2] < tolerance:
                # Make it transparent
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        
        img.putdata(newData)
        
        # Optional: Crop to content
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        img.save(output_path, "PNG")
        print(f"Processed {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# Process both
# Note: The generate_image tool saves to artifacts directory. 
# I need to find where they are. 
# Assuming they are saved in CWD or artifacts dir. 
# The tool description says "Saved as an artifact". 
# Usually, I can access them via the ImageName if I pass it to tools, 
# but for Python script I need absolute paths.
# I will assume they are in the Cwd/artifacts/ or I'll wait for the tool output to give me the path.
# For now, I'll write the script, but I might need to adjust paths after generation.

if __name__ == "__main__":
    # Placeholder paths - passed as args would be better but hardcoding for the specific task is faster
    # I'll rely on the tool output to know where the files are and then run this script with arguments.
    if len(sys.argv) > 2:
        remove_black_background(sys.argv[1], sys.argv[2])
