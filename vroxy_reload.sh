#!/bin/bash

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"
SCRIPT_DIR=$(pwd)
if pgrep tmux; then
    echo "Stopping Vroxy service"
    tmux kill-session -t vroxy
fi
if [[ "$CI" != "true" ]]; then
    echo "Checking for latest Vroxy updates"
    git pull --ff-only
fi
echo "Starting Vroxy service from $SCRIPT_DIR"
tmux new-session -d -s vroxy \; send-keys "python3 $SCRIPT_DIR/vroxy.py" Enter
echo "Vroxy service successfully started in a tmux session"