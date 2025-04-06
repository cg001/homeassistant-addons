import os
import paramiko
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, make_response
from datetime import datetime
import threading
import time
import json
import paho.mqtt.client as mqtt

# Create Flask app with static URL path to handle ingress subpath
app = Flask(__name__, static_url_path='')

# Configure for running behind a proxy with a path prefix (for Home Assistant ingress)
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Comprehensive CORS handling
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-Forwarded-For, X-Forwarded-Proto, X-Real-IP'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    return response
processed_files = set()
xml_data_list = []
last_update = None
data_lock = threading.Lock()  # Thread-safe Zugriff auf die Daten

SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USER = os.getenv("SFTP_USER")
SFTP_PASS = os.getenv("SFTP_PASS")
SFTP_DIR = os.getenv("SFTP_DIR")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "60"))  # Default to 60 seconds

# MQTT-Konfiguration
MQTT_BROKER = os.getenv("MQTT_BROKER", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "mqtt_loau")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "loau_685")
MQTT_TOPIC = "tankdaten"

# MQTT-Client einrichten
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="tankdaten_addon")  # Explizite client_id setzen und API Version 2 verwenden
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.enable_logger()  # Debugging aktivieren
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=30)  # Keep-Alive auf 30 Sekunden setzen
    mqtt_client.loop_start()
    print(f"✅ Verbunden mit MQTT-Broker: {MQTT_BROKER}:{MQTT_PORT}")
except Exception as e:
    print(f"❌ Fehler beim Verbinden mit MQTT-Broker: {e}")

template_path = os.path.join(os.path.dirname(__file__), "www", "index.html")
with open(template_path) as f:
    template_html = f.read()

def send_to_mqtt(data):
    """Sendet die geparsten Daten an MQTT."""
    try:
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        print(f"✅ Daten an MQTT gesendet: {len(data['transactions'])} Transaktionen")
    except Exception as e:
        print(f"❌ Fehler beim Senden an MQTT: {e}")

def fetch_newest_files():
    global processed_files, xml_data_list, last_update
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.chdir(SFTP_DIR)

        # Sortiere Dateien nach Änderungsdatum, neueste zuerst
        files = sorted(sftp.listdir_attr(), key=lambda x: x.st_mtime, reverse=True)
        new_data = []

        # Temporäre Liste für neue Dateien
        temp_processed = set()

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
                        quantity = txn.findtext("TransactionQuantity", "")
                        if quantity:
                            quantity = quantity.replace('.', ',')

                        transactions.append({
                            "number": txn.findtext("TransactionNumber", ""),
                            "timestamp": txn.findtext("TransactionStartDate", ""),
                            "dispenser": txn.findtext(".//DispenserNumber", ""),
                            "article": article_name,
                            "quantity": txn.findtext("TransactionQuantity", ""),
                            "license_plate": license_plate
                        })

                    if transactions:  # Nur hinzufügen wenn Transaktionen gefunden wurden
                        new_data.append({
                            "filename": f.filename,
                            "transactions": sorted(transactions, key=lambda x: x["timestamp"], reverse=True)
                        })
                        temp_processed.add(f.filename)

                if len(new_data) >= 20:  # Limit auf 20 Dateien
                    break
            except Exception as e:
                print("Fehler beim Parsen:", f.filename, str(e))

        sftp.close()
        transport.close()

        with data_lock:
            # Aktualisiere die processed_files nur mit erfolgreich verarbeiteten Dateien
            processed_files.update(temp_processed)

            # Füge neue Daten hinzu, ohne alte zu überschreiben
            for new_file in new_data:
                if new_file["filename"] not in [f["filename"] for f in xml_data_list]:
                    xml_data_list.append(new_file)

            # Sortiere alle Transaktionen nach Zeitstempel
            all_transactions = []
            for file_data in xml_data_list:
                all_transactions.extend(file_data["transactions"])

            # Sortiere nach Zeitstempel und erstelle neue Dateiliste
            sorted_transactions = sorted(all_transactions, key=lambda x: x["timestamp"], reverse=True)

            # Begrenze auf die neuesten 20 Transaktionen
            xml_data_list = [{
                "filename": "combined",
                "transactions": sorted_transactions[:20]
            }]

            # Sende Daten an MQTT
            send_to_mqtt(xml_data_list[0])

            last_update = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")

        return True
    except Exception as e:
        print("❌ Fehler beim SFTP-Zugriff:", str(e))
        return False

def background_refresh():
    """Background task für automatisches Refresh"""
    while True:
        time.sleep(REFRESH_INTERVAL)
        fetch_newest_files()

@app.route("/")
def index():
    # Add cache-control headers to prevent caching
    response = make_response(render_template_string(
        template_html,
        files=xml_data_list,
        last_update=last_update,
        refresh_interval=REFRESH_INTERVAL
    ))
    # Add CORS headers
    response = add_cors_headers(response)
    return response

@app.route("/api/data")
def get_data():
    """API endpoint für AJAX requests"""
    with data_lock:
        response = jsonify({
            "success": True,
            "files": xml_data_list,
            "last_update": last_update
        })
        # Add CORS headers
        response = add_cors_headers(response)
        return response

@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    """Endpoint für manuelles Refresh"""
    success = fetch_newest_files()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Wenn AJAX Request, JSON zurückgeben
        response = jsonify({
            "success": success,
            "files": xml_data_list,
            "last_update": last_update
        })
        # Add CORS headers
        response = add_cors_headers(response)
        return response

    # Wenn normaler Request, zur Hauptseite zurückleiten
    return redirect(url_for('index'))

# Handle OPTIONS requests for CORS preflight
@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-Forwarded-For, X-Forwarded-Proto, X-Real-IP'
    response.headers['Access-Control-Max-Age'] = '1728000'
    return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    return add_cors_headers(response)

if __name__ == "__main__":
    # Set initial timestamp
    last_update = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")

    # Fetch initial files
    fetch_newest_files()

    # Start background refresh thread
    refresh_thread = threading.Thread(target=background_refresh, daemon=True)
    refresh_thread.start()

    # Start the Flask app
    app.run(host="0.0.0.0", port=8088)
