
#!/bin/bash
echo "📡 Connecting to Raspberry Pi Log Viewer..."
sshpass -p 4200 ssh -t pi@192.168.1.50 "pkill -f bridge_v48.py; echo '🚀 Relaunching Bridge...'; python3 ~/behringer-mixer/bridge_v48.py"
