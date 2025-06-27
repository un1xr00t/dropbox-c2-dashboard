from flask import request, abort, Flask, render_template, send_from_directory
from pathlib import Path
import os
import re
from collections import defaultdict
from utils.parser import parse_sessions, parse_payloads, parse_loot, summarize_recon_files_ai

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
PAYLOAD_DIR = os.path.join(BASE_DIR, 'payloads')
LOOT_DIR = os.path.join(BASE_DIR, 'loot')
RECON_DIR = os.path.join(LOOT_DIR, 'recon')

# 🔐 IP Whitelist Logic
@app.before_request
def limit_remote_addr():
    allowed_ips = ['73.174.44.217', '163.114.130.129']
    if request.remote_addr not in allowed_ips:
        abort(403)

# 🔎 Open Ports Extractor
def extract_open_ports(recon_dir=RECON_DIR):
    recon_path = Path(recon_dir)
    port_map = defaultdict(set)
    ip_regex = re.compile(r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)")
    port_line = re.compile(r"^(\d+)/tcp\s+open")

    current_ip = None
    for file in sorted(recon_path.glob("*.txt")):
        try:
            lines = file.read_text(errors="ignore").splitlines()
        except:
            continue

        for line in lines:
            ip_match = ip_regex.search(line)
            if ip_match:
                current_ip = ip_match.group(1)
                continue

            port_match = port_line.match(line)
            if port_match and current_ip:
                port = int(port_match.group(1))
                if port in {21, 22, 23, 80, 139, 443, 445, 3306, 3389, 8080}:
                    port_map[port].add(current_ip)

    return {port: sorted(list(ips)) for port, ips in sorted(port_map.items())}

# 🧠 Home Route
@app.route('/')
def index():
    sessions = parse_sessions(LOG_DIR)
    payloads = parse_payloads(PAYLOAD_DIR)
    loot = parse_loot(LOOT_DIR)
    recon_summary = summarize_recon_files_ai()
    open_ports = extract_open_ports()

   
    return render_template(
        'index.html',
        sessions=sessions,
        payloads=payloads,
        loot=loot,
        recon_summary=recon_summary,
        open_ports=open_ports
    )


# 🔽 Serve Payloads + Loot
@app.route('/payloads/<path:filename>')
def serve_payload(filename):
    return send_from_directory(PAYLOAD_DIR, filename)

@app.route('/loot/recon/<path:filename>')
def serve_loot_file(filename):
    return send_from_directory(os.path.join(LOOT_DIR, 'recon'), filename)

@app.route('/loot/screens/<path:filename>')
def serve_screenshot(filename):
    return send_from_directory(os.path.join(LOOT_DIR, 'screens', 'screens'), filename)

# 🚀 Launch
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
