#!/bin/bash
mkdir -p ui_assets_sliced

BASE="/Users/gimdongseong/.gemini/antigravity/brain/7d881365-0c82-4ae7-965e-eaeafa58df40"
OUT="ui_assets_sliced"

# Function to slice one sheet (2 rows x 4 cols) using cropToHeightWidth H W and cropOffset Y X
# Image 1024x1024 -> Cell 512x256 (Height 512, Width 256)
# Actually let's assume 2 rows (512h) x 4 cols (256w)
H=512
W=256

process_sheet() {
    SRC=$1
    START_IDX=$2
    
    # Row 0
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 0 0    --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 0))).png"
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 0 256  --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 1))).png"
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 0 512  --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 2))).png"
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 0 768  --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 3))).png"
    
    # Row 1
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 512 0   --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 4))).png"
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 512 256 --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 5))).png"
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 512 512 --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 6))).png"
    sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 512 768 --out "$OUT/frame_$(printf "%02d" $(($START_IDX + 7))).png"
}

# 1. Part 1 (Steps 1-8)
process_sheet "$BASE/ui_match_1_seed_sprout_1765865300444.png" 1

# 2. Part 2 (Steps 9-16)
process_sheet "$BASE/ui_match_2_young_tree_1765865319198.png" 9

# 3. Part 3 (Steps 17-24)
process_sheet "$BASE/ui_match_3_tree_blooming_1765865343996.png" 17

# 4. Part 4 (Steps 25-32)
process_sheet "$BASE/ui_match_4_tree_finish_fixed_1765865781580.png" 25

echo "Slicing complete. Files in $OUT/"
