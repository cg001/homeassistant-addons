import os
import time
import json
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from sftp_handler import fetch_latest_xml  # Deine bestehende SFTP-Logik
from xml_parser import parse_xml_to_table  # Deine bestehende XML-Parsing-Logik

app = Flask(__name__)

# MQTT-Konfiguration
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.5.100")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "mqtt_user")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "mqtt_password")
MQTT_TOPIC = "tankdaten"

# MQTT-Client einrichten
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Globale Variable für die HTML-Tabelle
html_table = ""
last_processed_file = None

@app.route("/")
def index():
    global html_table
    return html_table

def send_to_mqtt(data):
    """Sendet die geparsten Daten an MQTT."""
    try:
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        print(f"✅ Daten an MQTT gesendet: {data}")
    except Exception as e:
        print(f"❌ Fehler beim Senden an MQTT: {e}")

def refresh_data():
    """Aktualisiert die Daten, wenn eine neue XML-Datei erkannt wird."""
    global html_table, last_processed_file

    # Neueste XML-Datei abrufen
    latest_file = fetch_latest_xml()
    if latest_file != last_processed_file:
        print(f"📂 Neue Datei erkannt: {latest_file}")
        last_processed_file = latest_file

        # XML-Datei parsen
        parsed_data = parse_xml_to_table(latest_file)
        html_table = render_template("table.html", data=parsed_data)

        # Daten an MQTT senden
        send_to_mqtt(parsed_data)
    else:
        print("🔄 Keine neue Datei gefunden.")

# Hintergrund-Thread für automatische Aktualisierung
def background_refresh():
    while True:
        refresh_data()
        time.sleep(int(os.getenv("REFRESH_INTERVAL", 3600)))

if __name__ == "__main__":
    import threading
    # Hintergrund-Thread starten
    threading.Thread(target=background_refresh, daemon=True).start()
    # Flask-Server starten
    app.run(host="0.0.0.0", port=8088)