#!/bin/bash

# Configuration
PI_USER="pi"
PI_HOST="192.168.1.11" # Update if different
REMOTE_DIR="/home/pi/behringer-mixer"

echo "🚀 Starting Deployment to Raspberry Pi ($PI_HOST)..."

# 1. Copy Python Scripts
echo "📂 Copying Scripts..."
scp -O osc_bridge_final.py artnet_bridge.py ptz_cam.py $PI_USER@$PI_HOST:$REMOTE_DIR/

# 2. Copy Service Files
echo "⚙️ Copying Service Files..."
scp -O osc_bridge.service artnet_bridge.service ptz_cam.service $PI_USER@$PI_HOST:/tmp/

# 3. Remote Execution: Move services and Reload
echo "🔄 Configuring Services on Pi..."
ssh $PI_USER@$PI_HOST << 'EOF'
    # Move services to system directory
    sudo mv /tmp/osc_bridge.service /etc/systemd/system/
    sudo mv /tmp/artnet_bridge.service /etc/systemd/system/
    sudo mv /tmp/ptz_cam.service /etc/systemd/system/

    # Disable old service if exists
    sudo systemctl disable --now behringer_wing.service 2>/dev/null || true
    
    # Reload Systemd
    sudo systemctl daemon-reload

    # Enable and Restart Services
    echo "   Starting Art-Net Bridge..."
    sudo systemctl enable --now artnet_bridge.service
    sudo systemctl restart artnet_bridge.service

    echo "   Starting OSC Bridge..."
    sudo systemctl enable --now osc_bridge.service
    sudo systemctl restart osc_bridge.service

    echo "   Starting PTZ Bridge..."
    sudo systemctl enable --now ptz_cam.service
    sudo systemctl restart ptz_cam.service

    # Show Status
    echo "📊 Service Status:"
    systemctl status artnet_bridge osc_bridge ptz_cam --no-pager | grep "Active:"
EOF

echo "✅ Deployment Complete!"
