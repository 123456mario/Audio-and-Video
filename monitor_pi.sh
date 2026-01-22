#!/bin/bash
echo "==============================================="
echo "       RASPBERRY PI UDP SNIFFER TOOL"
echo "==============================================="
echo "Target: 192.168.1.50"
echo "Password: 4200 (Type if asked)"
echo "-----------------------------------------------"

# 1. Cleanup conflicting processes
echo "[1/2] Stopping existing Art-Net services..."
ssh pi@192.168.1.50 "echo 4200 | sudo -S pkill -f artnet_bridge.py"
ssh pi@192.168.1.50 "echo 4200 | sudo -S pkill -f udp_sniffer.py"

echo ""
echo "[2/2] Starting UDP Sniffer on Port 10012..."
echo "Waiting for data from Xilica... (Press Ctrl+C to stop)"
echo "-----------------------------------------------"

# 2. Run Sniffer
ssh -t pi@192.168.1.50 "python3 -u /home/pi/behringer-mixer/udp_sniffer.py"
