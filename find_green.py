import os
import numpy as np
from PIL import Image

def find_green_images(directory):
    print(f"Scanning {directory} for green images...")
    candidates = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".png"):
                path = os.path.join(root, file)
                try:
                    img = Image.open(path).convert("RGB")
                    # Resize for speed and dominant color extraction
                    img_small = img.resize((50, 50))
                    arr = np.array(img_small)
                    
                    # Mean color of non-white/black pixels?
                    # Or just global mean
                    r_mean = np.mean(arr[:,:,0])
                    g_mean = np.mean(arr[:,:,1])
                    b_mean = np.mean(arr[:,:,2])
                    
                    # Simple heuristic for "Green"
                    # Green dominant and significantly higher than others
                    if g_mean > r_mean + 10 and g_mean > b_mean + 10:
                        candidates.append((file, (r_mean, g_mean, b_mean)))
                    # Also check for Forest Green (Dark Green)
                    # Low R, B, Mid/High G
                except:
                    pass
    
    for c in candidates:
        print(f"Found Green Candidate: {c[0]} - RGB: {c[1]}")

find_green_images("/Users/gimdongseong/Documents/GitHub/behringer-mixer/디자인")
