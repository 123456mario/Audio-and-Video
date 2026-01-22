#!/bin/bash
cd ~/behringer-mixer
if [ ! -d "venv" ]; then
    echo "--- Creating Virtual Environment ---"
    python3 -m venv venv
fi

echo "--- Activating Venv & Installing Deps (Offline) ---"
source venv/bin/activate
pip install --no-index --find-links ./pi_packages setuptools wheel
pip install --no-index --find-links ./pi_packages python-osc requests

echo "--- Starting OSC Bridge ---"
python osc_bridge.py
