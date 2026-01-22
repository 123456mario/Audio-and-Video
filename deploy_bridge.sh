
#!/bin/bash
echo "📡 Deploying bridge_v48.py to Raspberry Pi..."
scp bridge_v48.py pi@192.168.1.50:~/behringer-mixer/bridge_v48.py

if [ $? -eq 0 ]; then
    echo "✅ Deployment Successful!"
    echo "🚀 Running the bridge on Pi..."
    ssh -t pi@192.168.1.50 "python3 ~/behringer-mixer/bridge_v48.py"
else
    echo "❌ Deployment Failed. Please check your password or network."
fi
