
#!/bin/bash
echo "👀 Watching Bridge Logs (Ctrl+C to stop)..."
sshpass -p 4200 ssh -t pi@192.168.1.50 "tail -f ~/bridge.log"
