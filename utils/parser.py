import os
import re
from glob import glob
from datetime import datetime

OUI_MAP = {}

def load_oui_file():
    global OUI_MAP
    oui_path = os.path.join(os.path.dirname(__file__), '..', 'oui.txt')
    if not os.path.exists(oui_path):
        print("[-] OUI file not found at", oui_path)
        return

    with open(oui_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            match = re.match(r"^(?P<hex>[0-9A-F\-]{6,})\s+\(base 16\)\s+(?P<vendor>.+)$", line.strip())
            if match:
                hex_oui = match.group("hex").replace("-", "").upper()
                vendor = match.group("vendor").strip()
                OUI_MAP[hex_oui] = vendor

load_oui_file()

def get_mac_vendor(mac):
    if not mac:
        return "N/A"
    cleaned = mac.upper().replace(":", "").replace("-", "")[:6]
    return OUI_MAP.get(cleaned, "Unknown Device")

def parse_sessions(log_dir):
    sessions = []
    for folder in sorted(os.listdir(log_dir)):
        folder_path = os.path.join(log_dir, folder)
        if os.path.isdir(folder_path):
            log_file = os.path.join(folder_path, "log.txt")
            label_file = os.path.join(folder_path, "label.txt")
            label = None
            entries = []
            ip = None
            os_name = None
            timestamps = []

            if os.path.exists(label_file):
                with open(label_file) as f:
                    label = f.read().strip()

            if os.path.exists(log_file):
                with open(log_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        entries.append(line)

                        if not ip:
                            ip_match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', line)
                            if ip_match:
                                ip = ip_match.group(1)

                        if not os_name:
                            if "Windows" in line:
                                os_name = "Windows"
                            elif "Linux" in line:
                                os_name = "Linux"
                            elif "Android" in line:
                                os_name = "Android"
                            elif "Mac" in line or "Darwin" in line:
                                os_name = "macOS"

                        timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
                        if timestamp_match:
                            try:
                                ts = datetime.strptime(timestamp_match.group(0), "%Y-%m-%d %H:%M:%S")
                                timestamps.append(ts)
                            except:
                                pass

            sessions.append({
                'folder': folder,
                'label': label or "Unlabeled",
                'log': entries,
                'ip': ip or "Unknown",
                'os': os_name or "Unknown",
                'first_seen': min(timestamps).strftime("%Y-%m-%d %H:%M:%S") if timestamps else "N/A",
                'last_seen': max(timestamps).strftime("%Y-%m-%d %H:%M:%S") if timestamps else "N/A"
            })
    return sessions

def parse_payloads(payload_dir):
    payloads = []
    for filename in sorted(os.listdir(payload_dir)):
        full_path = os.path.join(payload_dir, filename)
        if os.path.isfile(full_path):
            payloads.append({
                'name': filename,
                'size_kb': os.path.getsize(full_path) // 1024
            })
    return payloads

def parse_loot(loot_dir):
    recon_dir = os.path.join(loot_dir, 'recon')
    screens_dir = os.path.join(loot_dir, 'screens', 'screens')

    loot = {
        'recon': [],
        'screens': []
    }

    if os.path.exists(recon_dir):
        for filename in sorted(os.listdir(recon_dir)):
            full_path = os.path.join(recon_dir, filename)
            if os.path.isfile(full_path):
                loot['recon'].append(filename)

    if os.path.exists(screens_dir):
        for filename in sorted(os.listdir(screens_dir)):
            if filename.lower().endswith('.png'):
                loot['screens'].append(filename)

    return loot

def summarize_recon_files_ai():
    loot_dir = "loot/recon"
    summaries = []

    for filename in os.listdir(loot_dir):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(loot_dir, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        hosts = []
        current_host = None

        for line in lines:
            line = line.strip()

            ip_match = re.search(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', line)
            port_match = re.search(r'^(\d+)/tcp\s+open\s+(\S+)', line)
            mac_match = re.search(r'MAC Address: ([0-9A-Fa-f:]{17})', line)

            if ip_match:
                print(f"[FOUND IP] {ip_match.group(1)} in {filename}")
                if current_host:
                    hosts.append(current_host)
                current_host = {
                    "ip": ip_match.group(1),
                    "ports": [],
                    "mac": None,
                    "device_type": "Unknown Device"
                }

            elif port_match and current_host:
                port = port_match.group(1)
                service = port_match.group(2)
                current_host["ports"].append(f"{port}/{service}")

            elif mac_match and current_host:
                mac = mac_match.group(1)
                current_host["mac"] = mac
                current_host["device_type"] = get_mac_vendor(mac)

        if current_host:
            hosts.append(current_host)
        host_ips = [h["ip"] for h in hosts]
        print(f"[SUMMARY DEBUG] {filename} → {len(hosts)} hosts: {host_ips if hosts else 'SKIPPED'}")

        summaries.append({
            "filename": filename,
            "hosts": hosts
        })

    print("\n[FINAL DEBUG] These files made it into recon_summary:")
    for s in summaries:
        print(f"  → {s['filename']} ({len(s['hosts'])} hosts)")

    return summaries
