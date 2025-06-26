
# 🧠 C2Ghost Dashboard – GitHub Writeup

> Part of the [Red Teaming Dropbox project](https://github.com/un1xr00t/red-teaming-dropbox)
> 
![image](https://github.com/user-attachments/assets/bbb50cbb-180a-4761-bfc2-72d371359be6)

C2Ghost is a Flask-based dashboard interface for visualizing red team operations data collected by the Red Teaming Dropbox (Raspberry Pi running Kali Linux). This dashboard runs on the Linode C2 server and synchronizes with the Dropbox to render parsed payloads, recon results, session logs, and screenshots — all dynamically.

---

## 📁 Project Directory Overview

**Linode Server Path:** `~/c2ghost/`

```bash
c2ghost/
├── c2ghost.py                  # Main Flask application
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html               # Base layout
│   └── index.html              # Dashboard page
├── static/                     # CSS, JS, images
│   └── style.css               # Custom dashboard styles
├── utils/                      # Python helpers
│   ├── __init__.py
│   └── parser.py               # Parses recon logs & payloads
├── payloads/                   # Uploaded payloads (auto-synced)
│   └── <files>
├── logs/                       # Session logs
│   └── <*.log>
├── loot/                       # Post-exploitation loot
│   ├── recon/                  # Nmap/CME/etc. output
│   │   └── *.txt
│   └── screens/                # Screenshot images
```

---

## 🔄 Async Sync with Raspberry Pi Dropbox

The Red Teaming Dropbox (Raspberry Pi running Kali) syncs with the Linode C2 server using passwordless SSH and a custom sync script.

### ✅ 1. Enable Passwordless SSH to Linode
To avoid login prompts every time:

🔑 On your Pi:
```bash
ssh-keygen -t rsa
# Press Enter through all prompts
ssh-copy-id root@<LINODE_IP>
```
Then test:
```bash
ssh root@<LINODE_IP>
# Should log in without password prompt
```

### ✅ 2. Create the Sync Script
Save the following as `sync-c2ghost.sh` on your Pi:

```bash
#!/bin/bash

LINODE_IP="your-linode-ip-here"
REMOTE_DIR="/root/c2ghost"

echo "[*] Syncing logs..."
rsync -avzu ~/logs/ root@$LINODE_IP:$REMOTE_DIR/logs/

echo "[*] Syncing payloads..."
rsync -avzu ~/payloads/ root@$LINODE_IP:$REMOTE_DIR/payloads/

echo "[*] Syncing loot..."
rsync -avzu ~/loot/ root@$LINODE_IP:$REMOTE_DIR/loot/

echo "[✓] Sync complete."
```

Make it executable and run it:
```bash
chmod +x sync-c2ghost.sh
./sync-c2ghost.sh
```

> This syncs only new or updated files, preserving existing ones.

### ✅ 3. Add to Cron (Optional)
To run it every 10 minutes (whatever interval you'd like):
```bash
crontab -e
```
Add:
```bash
*/10 * * * * /home/kali/sync-c2ghost.sh
```

--- 

## 🧩 Flask Application Logic

### 🔥 App Routes (in `c2ghost.py`):
- `/` → Main dashboard route (renders recon + payload cards)
- `/payloads/<filename>` → Serve payloads
- `/loot/recon/<filename>` → Serve recon file text
- `/loot/screens/<filename>` → Serve screenshot images

### 🧠 Recon Summary Parser – `summarize_recon_files_ai()`
Reads `loot/recon/*.txt` and extracts:
```json
[
  {
    "filename": "nmap_deep_10.0.0.80.txt",
    "hosts": [
      {
        "ip": "10.0.0.80",
        "ports": [80, 443],
        "mac": "00:11:22:33:44:55",
        "device_type": "Cisco Systems"
      }
    ]
  }
]
```

### 📡 `extract_open_ports()`
Pulls a list of interesting ports from all recon files for a top summary.

---

## 🖼️ Template Rendering: `templates/index.html`

- Loops over recon summaries with `{% for recon in recon_summary %}`
- Each summary becomes a card (up to 5 shown by default)
- Includes toggles: “Show All” and “Collapse”

```html
<div class="recon-card {% if loop.index > 5 %}hidden{% endif %}">
  <!-- Recon content -->
</div>
```

---

## 🎨 Styling: `static/style.css`

- `.card-grid`: Responsive layout
- `.mono-font`: Terminal-style text
- `.hidden`: Toggled with JS
- `.toggle-btn`: Button styles
- `.ascii-banner`: Retro-style header (Mr. Robot vibes)

---

## 📊 Dynamic Recon Visualization

Buttons:
```html
<button id="showBtn" onclick="showAllRecon()">Show All</button>
<button id="collapseBtn" onclick="collapseRecon()">Collapse</button>
```
JavaScript Functions:
```js
function showAllRecon() {
  document.querySelectorAll('.recon-card').forEach((card, i) => {
    card.classList.remove('hidden');
  });
  document.getElementById('showBtn').style.display = 'none';
  document.getElementById('collapseBtn').style.display = 'inline-block';
}

function collapseRecon() {
  document.querySelectorAll('.recon-card').forEach((card, i) => {
    if (i >= 5) card.classList.add('hidden');
  });
  document.getElementById('collapseBtn').style.display = 'none';
  document.getElementById('showBtn').style.display = 'inline-block';
}
```

---

## ✅ What It Does

This dashboard lets red teamers:
- 🔍 View parsed recon scans (Nmap, CME)
- ⚓ Access dropped payloads
- 👀 Browse screenshots from sessions
- 📄 View active session logs
- 🔁 Auto-sync new files from field Dropbox

---

## 🧪 Example Recon File Format (Supported)

```text
Nmap scan report for 10.0.0.80
Host is up.
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 10.0
80/tcp   open  http    Apache 2.4.57
MAC Address: 00:11:22:33:44:55 (Cisco Systems)
```

---

## 📥 Requirements

- Flask
- Python 3.10+
- `rsync`
- Passwordless SSH to Linode
- File structure must match:
  - `/home/kali/loot/recon/*.txt`
  - `/home/kali/payloads/`
  - `/home/kali/logs/`
  - `/home/kali/loot/screens/`

---

## 🚀 Get Started

```bash
git clone https://github.com/un1xr00t/red-teaming-dropbox
cd c2ghost
pip install flask
python3 c2ghost.py
```

Then navigate to `http://<LINODE_IP>:5000`

---

## 📌 Credits
- Project by [un1xr00t](https://github.com/un1xr00t)
- Dashboard by William (C2Ghost)
- Powered by Flask, rsync, and red team pain

---

> For full Raspberry Pi Dropbox deployment steps, refer to the main repo: https://github.com/un1xr00t/red-teaming-dropbox
