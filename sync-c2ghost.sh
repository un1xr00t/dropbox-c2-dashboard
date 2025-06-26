#!/bin/bash

# IP address of your Linode server (update this!)
LINODE_IP="your-linode-ip-here"
REMOTE_DIR="/root/c2ghost"

# Make sure passwordless SSH is set up beforehand with: ssh-copy-id root@$LINODE_IP

echo "[*] Syncing logs..."
rsync -avzu ~/logs/ root@$LINODE_IP:$REMOTE_DIR/logs/

echo "[*] Syncing payloads..."
rsync -avzu ~/payloads/ root@$LINODE_IP:$REMOTE_DIR/payloads/

echo "[*] Syncing loot..."
rsync -avzu ~/loot/ root@$LINODE_IP:$REMOTE_DIR/loot/

echo "[✓] Sync complete."
