#!/bin/bash
# Activate venv and run bridge
cd "$(dirname "$0")"
source venv/bin/activate

echo "🎵 Starting Xilica-Wing-PTZ Bridge..."
# Ensure permissions
chmod +x osc_bridge.py

# Run with python -u (unbuffered) for logs
python -u osc_bridge.py
