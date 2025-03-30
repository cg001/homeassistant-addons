import os
import paramiko
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
processed_files = set()
data_rows = []

SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USER = os.getenv("SFTP_USER")
SFTP_PASS = os.getenv("SFTP_PASS")
SFTP_DIR = os.getenv("SFTP_DIR")

template_path = os.path.join(os.path.dirname(__file__), "www", "index.html")
with open(template_path) as f:
    template_html = f.read()

def parse_xml(content):
    root = ET.fromstring(content)
    rows = []
    for txn in root.findall(".//Transaction"):
        try:
            rows.append({
                "nr": txn.findtext("Number", "-"),
                "timestamp": txn.findtext("DateTime", "-"),
                "pump": txn.findtext("Pump", "-"),
                "product": txn.findtext("Product", "-"),
                "amount": txn.findtext("Quantity", "-"),
                "plate": txn.findtext("Plate", "-"),
            })
        except Exception as e:
            print("❌ Fehler beim Parsen einzelner TXN:", str(e))
    return rows

def fetch_newest_files():
    global processed_files, data_rows
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.chdir(SFTP_DIR)
        files = sorted(sftp.listdir_attr(), key=lambda x: x.st_mtime, reverse=True)
        new_entries = []

        for f in files:
            if not f.filename.lower().endswith(".xml") or f.filename in processed_files:
                continue
            try:
                with sftp.open(f.filename) as file_obj:
                    content = file_obj.read().decode()
                    parsed = parse_xml(content)
                    if parsed:
                        new_entries.extend(parsed)
                processed_files.add(f.filename)
                if len(new_entries) + len(data_rows) >= 20:
                    break
            except Exception as e:
                print("Fehler beim Parsen:", f.filename, str(e))

        sftp.close()
        transport.close()
        data_rows = sorted(new_entries + data_rows, key=lambda x: x["timestamp"], reverse=True)[:100]
    except Exception as e:
        print("❌ Fehler beim SFTP-Zugriff:", str(e))

@app.route("/")
def index():
    return render_template_string(template_html, data=data_rows[:20], update_time=datetime.now().strftime("%d.%m.%Y, %H:%M:%S"))

@app.route("/refresh", methods=["POST"])
def refresh():
    fetch_newest_files()
    return redirect(url_for("index"))

if __name__ == "__main__":
    fetch_newest_files()
    app.run(host="0.0.0.0", port=8080)
