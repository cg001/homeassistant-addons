import os
import paramiko
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
processed_files = set()
xml_data_list = []
last_update = None

SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USER = os.getenv("SFTP_USER")
SFTP_PASS = os.getenv("SFTP_PASS")
SFTP_DIR = os.getenv("SFTP_DIR")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "60"))  # Default to 60 seconds

template_path = os.path.join(os.path.dirname(__file__), "www", "index.html")
with open(template_path) as f:
    template_html = f.read()

def fetch_newest_files():
    global processed_files, xml_data_list
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.chdir(SFTP_DIR)
        files = sorted(sftp.listdir_attr(), key=lambda x: x.st_mtime, reverse=True)
        new_data = []

        for f in files:
            if not f.filename.lower().endswith(".xml") or f.filename in processed_files:
                continue
            try:
                with sftp.open(f.filename) as file_obj:
                    content = file_obj.read().decode()
                    root = ET.fromstring(content)
                    transactions = []
                    for txn in root.findall(".//Transaction"):
                        # Map article number to fuel type
                        article_number = txn.findtext(".//ArticleNumber", "")
                        article_name = "MOGAS"  # Default
                        if article_number == "1":
                            article_name = "AVGAS"
                        
                        # Get license plate from MediaData
                        license_plate = ""
                        media_data = txn.find(".//MediaData")
                        if media_data is not None:
                            license_plate = media_data.findtext("AdditionalEntry", "")
                        
                        transactions.append({
                            "number": txn.findtext("TransactionNumber", ""),
                            "timestamp": txn.findtext("TransactionStartDate", ""),
                            "dispenser": txn.findtext(".//DispenserNumber", ""),
                            "article": article_name,
                            "quantity": txn.findtext("TransactionQuantity", ""),
                            "license_plate": license_plate
                        })
                    new_data.append({
                        "filename": f.filename,
                        "transactions": transactions
                    })
                processed_files.add(f.filename)
                if len(new_data) + len(xml_data_list) >= 20:
                    break
            except Exception as e:
                print("Fehler beim Parsen:", f.filename, str(e))

        sftp.close()
        transport.close()
        xml_data_list = new_data + xml_data_list
    except Exception as e:
        print("❌ Fehler beim SFTP-Zugriff:", str(e))

@app.route("/")
def index():
    # Add cache-control headers to prevent caching
    response = render_template_string(
        template_html, 
        files=xml_data_list, 
        last_update=last_update,
        refresh_interval=REFRESH_INTERVAL
    )
    return response

@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    # Always update the timestamp first
    global last_update
    last_update = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    
    # Then fetch new files
    fetch_newest_files()
    
    # Redirect to the index page
    return redirect("/")

if __name__ == "__main__":
    # Set initial timestamp
    last_update = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    
    # Fetch initial files
    fetch_newest_files()
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=8080)
