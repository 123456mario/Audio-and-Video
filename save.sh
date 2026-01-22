#!/bin/bash
# One-click save script for Behringer Mixer Project

echo "========================================"
echo " 💾 Saving your work to GitHub..."
echo "========================================"

# Add all changes
git add .

# Commit with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Work saved on $TIMESTAMP"

# Push to GitHub
echo "🚀 Uploading to Cloud..."
git push

echo "========================================"
echo " ✅ Done! Your code is safe."
echo "========================================"
