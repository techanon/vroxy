#!/bin/bash
cd /var/vroxy
echo "Stopping Vroxy service"
tmux kill-session -t vroxy
echo "Checking for latest Vroxy updates"
git pull
echo "Starting Vroxy service"
tmux new-session -d -s vroxy \; send-keys "python3 /var/vroxy/vroxy.py" Enter
echo "Vroxy service successfully started in a tmux session"