#!/usr/bin/env bash
cd /var/qroxy
echo "Stopping Qroxy service"
tmux kill-session -t qroxy
echo "Checking for latest Qroxy updates"
git pull
echo "Starting Qroxy service"
tmux new-session -d -s qroxy \; send-keys "python3 /var/qroxy/qroxy.py" Enter
echo "Qroxy service successfully started in a tmux session"