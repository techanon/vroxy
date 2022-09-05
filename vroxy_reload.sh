#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
SCRIPT_DIR=$(pwd)
echo "Stopping Vroxy service"
tmux kill-session -t vroxy
echo "Checking for latest Vroxy updates"
git pull --ff-only
echo "Starting Vroxy service from $SCRIPT_DIR"
tmux new-session -d -s vroxy \; send-keys "python3 $SCRIPT_DIR/vroxy.py" Enter
echo "Vroxy service successfully started in a tmux session"