import os
import paramiko
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from datetime import datetime
import threading
import time
import json
import paho.mqtt.client as mqtt

app = Flask(__name__)
processed_files = set()
xml_data_list = []
last_update = None
data_lock = threading.Lock()  # Thread-safe Zugriff auf die Daten

# SFTP-Konfiguration
SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USER = os.getenv("SFTP_USER")
SFTP_PASS = os.getenv("SFTP_PASS")
SFTP_DIR = os.getenv("SFTP_DIR")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "60"))  # Default to 60 seconds

# MQTT-Konfiguration
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.5.100")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "mqtt_user")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "mqtt_password")
MQTT_TOPIC = "tankdaten"

# MQTT-Client einrichten
mqtt_client = mqtt.Client(client_id="tankdaten_addon", protocol=mqtt.MQTTv5)  # Aktualisierte API-Version
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# MQTT-Verbindung mit Fehlerbehandlung
mqtt_connected = False
def connect_mqtt():
    global mqtt_connected
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        mqtt_connected = True
        print(f"✅ Verbunden mit MQTT-Broker: {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"❌ Fehler beim Verbinden mit MQTT-Broker: {e}")
        mqtt_connected = False

connect_mqtt()

template_path = os.path.join(os.path.dirname(__file__), "www", "index.html")
with open(template_path) as f:
    template_html = f.read()

def send_to_mqtt(data):
    """Sendet die geparsten Daten an MQTT."""
    global mqtt_connected
    if not mqtt_connected:
        print("⚠️ Keine MQTT-Verbindung verfügbar, versuche neu zu verbinden...")
        connect_mqtt()
    if mqtt_connected:
        try:
            mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
            print(f"✅ Daten an MQTT gesendet: {len(data['transactions'])} Transaktionen")
        except Exception as e:
            print(f"❌ Fehler beim Senden an MQTT: {e}")
            mqtt_connected = False

# ... [Dein bestehender Code für fetch_newest_files() bleibt unverändert] ...

def background_refresh():
    """Background task für automatisches Refresh"""
    while True:
        fetch_newest_files()
        time.sleep(REFRESH_INTERVAL)

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

@app.route("/api/data")
def get_data():
    """API endpoint für AJAX requests"""
    with data_lock:
        return jsonify({
            "success": True,
            "files": xml_data_list,
            "last_update": last_update
        })

@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    """Endpoint für manuelles Refresh"""
    success = fetch_newest_files()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Wenn AJAX Request, JSON zurückgeben
        return jsonify({
            "success": success,
            "files": xml_data_list,
            "last_update": last_update
        })

    # Wenn normaler Request, zur Hauptseite zurückleiten
    return redirect("/")

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