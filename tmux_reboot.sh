#!/usr/bin/env bash
cd /var/qroxy
# kill existing
tmux kill-session -t qroxy
# get the latest updates
git pull
# start new
tmux new-session -d -s qroxy \; send-keys "python3 /var/qroxy/qroxy.py" Enter