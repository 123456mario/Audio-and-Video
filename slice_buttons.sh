#!/bin/bash
mkdir -p button_assets_sliced

SRC="/Users/gimdongseong/.gemini/antigravity/brain/7d881365-0c82-4ae7-965e-eaeafa58df40/btn_fill_sequence_1765868221809.png"
OUT="button_assets_sliced"

# Image is 1024x1024. 
# 6 steps.
# Assuming 3 Rows x 2 Cols.
# Col Width = 512
# Row Height = 341 (approx)

W=512
H=341

# Row 1
sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 0 0    --out "$OUT/btn_step_1.png"
sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 0 512  --out "$OUT/btn_step_2.png"

# Row 2
sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 341 0   --out "$OUT/btn_step_3.png"
sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 341 512 --out "$OUT/btn_step_4.png"

# Row 3
sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 682 0   --out "$OUT/btn_step_5.png"
sips -s format png "$SRC" --cropToHeightWidth $H $W --cropOffset 682 512 --out "$OUT/btn_step_6.png"

echo "Button slicing complete. Files in $OUT/"
