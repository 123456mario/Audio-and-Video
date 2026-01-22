#!/bin/bash
echo "🚀 Setting up Bridge on Raspberry Pi..."

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 could not be found. Please install python3."
    exit 1
fi

# Create Virtual Env
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and Install
echo "⬇️ Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Setup Complete!"
echo "👉 Run './run_bridge.sh' to start."
