#!/bin/bash
# Kill any existing python processes for these scripts to avoid port conflicts
pkill -f test_wing_server.py
pkill -f osc_bridge.py

echo "Starting Hybrid Mode (Virtual Wing + Real Xilica)..."

# Start Wing Mock Server in background
python3 test_wing_server.py &
WING_PID=$!
echo "✅ Started Wing Mock Server (PID: $WING_PID)"

# Wait a moment for server to bind
sleep 1

# Start Bridge
echo "✅ Starting Bridge..."
python3 osc_bridge.py

# When Bridge exits, kill Wing Server
kill $WING_PID
