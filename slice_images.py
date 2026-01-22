import os
from PIL import Image

# Configuration
base_dir = "/Users/gimdongseong/.gemini/antigravity/brain/7d881365-0c82-4ae7-965e-eaeafa58df40"
output_dir = os.path.join(base_dir, "ui_assets_sliced")
os.makedirs(output_dir, exist_ok=True)

# Source Files (The Minimal/Fixed set)
source_files = [
    "ui_match_1_seed_sprout_1765865300444.png",      # Steps 1-8
    "ui_match_2_young_tree_1765865319198.png",       # Steps 9-16
    "ui_match_3_tree_blooming_1765865343996.png",    # Steps 17-24
    "ui_match_4_tree_finish_fixed_1765865781580.png" # Steps 25-32
]

def slice_sheet(sheet_path, start_index):
    try:
        img = Image.open(sheet_path)
        width, height = img.size
        
        # Assume 2 rows, 4 columns (Standard for these prompts)
        # Adjust if necessary based on image aspect ratio? 
        # Usually these gens are square or 1:1, laid out in grid.
        # Let's assume standard grid subdivision.
        
        rows = 2
        cols = 4
        
        step_w = width / cols
        step_h = height / rows
        
        current_idx = start_index
        
        # Process row by row, col by col
        for r in range(rows):
            for c in range(cols):
                left = c * step_w
                upper = r * step_h
                right = left + step_w
                lower = upper + step_h
                
                cropped = img.crop((left, upper, right, lower))
                
                # Save
                filename = f"tree_step_{current_idx:02d}.png"
                out_path = os.path.join(output_dir, filename)
                cropped.save(out_path)
                print(f"Saved: {out_path}")
                
                current_idx += 1
                
    except Exception as e:
        print(f"Error processing {sheet_path}: {e}")

# Run
current_step = 1
for fname in source_files:
    full_path = os.path.join(base_dir, fname)
    if os.path.exists(full_path):
        print(f"Processing sheet: {fname} starting at step {current_step}")
        slice_sheet(full_path, current_step)
        current_step += 8
    else:
        print(f"File not found: {full_path}")
