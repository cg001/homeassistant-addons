#!/usr/bin/env python3
"""
Tank Data Reader for Home Assistant

This script connects to an SFTP server, downloads the newest XML files,
extracts specific data, generates an HTML page, and publishes data to MQTT.

Usage:
    python tank_data_reader.py
"""

import os
import sys
import paramiko
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import logging
import paho.mqtt.client as mqtt
from pathlib import Path

# Configure logging based on environment variable
LOG_LEVELS = {
    'trace': logging.DEBUG,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'fatal': logging.CRITICAL
}

def setup_logging():
    """Set up logging based on environment variables."""
    log_level_str = os.environ.get('LOG_LEVEL', 'info').lower()
    log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger('TankDataReader')
    logger.setLevel(log_level)
    
    logger.debug(f"Logging initialized at level: {log_level_str}")
    return logger

logger = setup_logging()

# Get configuration from environment variables
SFTP_HOST = os.environ.get('SFTP_HOST', '192.168.5.205')
SFTP_PORT = int(os.environ.get('SFTP_PORT', '22'))
SFTP_USERNAME = os.environ.get('SFTP_USERNAME', 'tankdaten')
SFTP_PASSWORD = os.environ.get('SFTP_PASSWORD', 'fsv2000')
SFTP_PATH = os.environ.get('SFTP_PATH', '/DiskC/Datatransfers/Upload/Data')

MQTT_HOST = os.environ.get('MQTT_HOST', 'core-mosquitto')
MQTT_PORT = int(os.environ.get('MQTT_PORT', '1883'))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_TOPIC_PREFIX = os.environ.get('MQTT_TOPIC_PREFIX', 'tank_data')

# Local Configuration
DATA_DIR = '/data/tank_data'
OUTPUT_FILE = '/app/www/index.html'
MAX_FILES = 10

def ensure_directory_exists(directory):
    """Ensure that the specified directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

def connect_to_sftp():
    """Connect to the SFTP server and return the SFTP client."""
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        logger.info(f"Connecting to SFTP server {SFTP_HOST}:{SFTP_PORT}...")
        ssh.connect(
            hostname=SFTP_HOST,
            port=SFTP_PORT,
            username=SFTP_USERNAME,
            password=SFTP_PASSWORD
        )
        
        # Open SFTP session
        sftp = ssh.open_sftp()
        logger.info("Successfully connected to SFTP server")
        return ssh, sftp
    except Exception as e:
        logger.error(f"Failed to connect to SFTP server: {e}")
        return None, None

def get_newest_files(sftp, path, max_files=10):
    """Get the newest files from the SFTP server."""
    try:
        # List all files in the directory
        logger.info(f"Listing files in {path}...")
        file_list = sftp.listdir_attr(path)
        
        # Filter for XML files and sort by modification time (newest first)
        xml_files = [f for f in file_list if f.filename.lower().endswith('.xml')]
        xml_files.sort(key=lambda f: f.st_mtime, reverse=True)
        
        # Get the newest files
        newest_files = xml_files[:max_files]
        logger.info(f"Found {len(newest_files)} newest XML files")
        
        return newest_files
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return []

def download_files(sftp, remote_path, files, local_dir):
    """Download files from the SFTP server."""
    downloaded_files = []
    
    for file_attr in files:
        remote_file = f"{remote_path}/{file_attr.filename}"
        local_file = f"{local_dir}/{file_attr.filename}"
        
        try:
            logger.info(f"Downloading {remote_file} to {local_file}...")
            sftp.get(remote_file, local_file)
            downloaded_files.append(local_file)
            logger.info(f"Successfully downloaded {file_attr.filename}")
        except Exception as e:
            logger.error(f"Failed to download {file_attr.filename}: {e}")
    
    return downloaded_files

def parse_xml_file(file_path):
    """Parse an XML file and extract the required data."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract data
        transaction_data = {}
        
        # Find the transaction element - could be directly under root or under Body
        transaction = root.find('.//Transaction')
        if transaction is None:
            logger.error(f"No Transaction element found in {file_path}")
            return None
        
        # Find the transaction number
        transaction_number = transaction.find('./TransactionNumber')
        if transaction_number is not None:
            transaction_data['TransactionNumber'] = transaction_number.text
        else:
            transaction_data['TransactionNumber'] = 'N/A'
        
        # Find the transaction start date
        transaction_start_date = transaction.find('./TransactionStartDate')
        if transaction_start_date is not None:
            # Convert from YYYY-MM-DD HH:MM:SS to DD.MM.YYYY HH:MM:SS for display
            try:
                date_obj = datetime.strptime(transaction_start_date.text, '%Y-%m-%d %H:%M:%S')
                formatted_date = date_obj.strftime('%d.%m.%Y %H:%M:%S')
                transaction_data['TransactionStartDate'] = formatted_date
                # Also store the original date for sorting
                transaction_data['RawDate'] = date_obj.isoformat()
            except ValueError:
                # If the date is already in DD.MM.YYYY format, use it as is
                transaction_data['TransactionStartDate'] = transaction_start_date.text
                try:
                    date_obj = datetime.strptime(transaction_start_date.text, '%d.%m.%Y %H:%M:%S')
                    transaction_data['RawDate'] = date_obj.isoformat()
                except ValueError:
                    transaction_data['RawDate'] = transaction_start_date.text
        else:
            transaction_data['TransactionStartDate'] = 'N/A'
            transaction_data['RawDate'] = '1970-01-01T00:00:00'
        
        # Find the dispenser number - might be nested under DispenserData
        dispenser_number = transaction.find('.//DispenserNumber')
        if dispenser_number is not None:
            transaction_data['DispenserNumber'] = dispenser_number.text
        else:
            transaction_data['DispenserNumber'] = 'N/A'
        
        # Find the article number - might be nested under ArticleData
        article_number = transaction.find('.//ArticleNumber')
        if article_number is not None:
            # Translate article numbers to fuel types
            if article_number.text == '1':
                transaction_data['ArticleNumber'] = 'AVGAS'
                transaction_data['RawArticleNumber'] = '1'
            elif article_number.text == '2':
                transaction_data['ArticleNumber'] = 'MOGAS'
                transaction_data['RawArticleNumber'] = '2'
            else:
                transaction_data['ArticleNumber'] = article_number.text
                transaction_data['RawArticleNumber'] = article_number.text
        else:
            transaction_data['ArticleNumber'] = 'N/A'
            transaction_data['RawArticleNumber'] = 'N/A'
        
        # Find the transaction quantity
        transaction_quantity = transaction.find('./TransactionQuantity')
        if transaction_quantity is not None:
            transaction_data['TransactionQuantity'] = transaction_quantity.text
            try:
                transaction_data['RawQuantity'] = float(transaction_quantity.text)
            except ValueError:
                transaction_data['RawQuantity'] = 0.0
        else:
            transaction_data['TransactionQuantity'] = 'N/A'
            transaction_data['RawQuantity'] = 0.0
        
        # Find the kennzeichen (license plate) - might be nested under MediaData
        additional_entry = transaction.find('.//AdditionalEntry')
        if additional_entry is not None:
            transaction_data['Kennzeichen'] = additional_entry.text
        else:
            transaction_data['Kennzeichen'] = 'N/A'
        
        logger.info(f"Successfully parsed {file_path}")
        return transaction_data
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        return None

def generate_html(data_list):
    """Generate an HTML page from the extracted data."""
    current_time = datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
    current_year = datetime.now().year
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tankdaten Übersicht</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .header-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .last-update {{
            text-align: right;
            font-style: italic;
            color: #7f8c8d;
        }}
        .reload-button {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .reload-button:hover {{
            background-color: #2980b9;
        }}
        .status-message {{
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            color: #2c3e50;
            display: none;
        }}
        .spinner {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: white;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        tr:hover {{
            background-color: #f1f9ff;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even):hover {{
            background-color: #e9f7fe;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        @media (max-width: 768px) {{
            table {{
                display: block;
                overflow-x: auto;
            }}
            th, td {{
                padding: 8px 10px;
                font-size: 0.9em;
            }}
        }}
    </style>
    <script>
        function reloadData() {{
            // Show loading message and spinner
            const button = document.getElementById('reload-button');
            const statusElement = document.getElementById('status-message');
            
            button.innerHTML = '<span class="spinner"></span> Lade Daten...';
            button.disabled = true;
            statusElement.textContent = 'Verbinde mit SFTP-Server...';
            statusElement.style.display = 'block';
            
            // Send request to the server to reload data
            fetch('/reload')
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        statusElement.textContent = 'Daten erfolgreich aktualisiert! Lade Seite...';
                        // Reload the page after a short delay to show the success message
                        setTimeout(() => {{
                            location.reload();
                        }}, 1000);
                    }} else {{
                        statusElement.textContent = 'Fehler: ' + data.message;
                        button.innerHTML = 'RELOAD';
                        button.disabled = false;
                    }}
                }})
                .catch(error => {{
                    statusElement.textContent = 'Fehler: ' + error.message;
                    button.innerHTML = 'RELOAD';
                    button.disabled = false;
                }});
        }}
    </script>
</head>
<body>
    <h1>Tankdaten Übersicht</h1>
    <div class="header-container">
        <button id="reload-button" class="reload-button" onclick="reloadData()">RELOAD</button>
        <div class="last-update">Letzte Aktualisierung: {current_time}</div>
    </div>
    <div id="status-message" class="status-message"></div>
    <table>
        <thead>
            <tr>
                <th>Nummer</th>
                <th>Datum + Uhrzeit</th>
                <th>Säulennummer</th>
                <th>Artikel</th>
                <th>Menge (Liter)</th>
                <th>Kennzeichen</th>
            </tr>
        </thead>
        <tbody>
"""

    # Add data rows
    for data in data_list:
        if data:
            html += f"""
            <tr>
                <td>{data.get('TransactionNumber', 'N/A')}</td>
                <td>{data.get('TransactionStartDate', 'N/A')}</td>
                <td>{data.get('DispenserNumber', 'N/A')}</td>
                <td>{data.get('ArticleNumber', 'N/A')}</td>
                <td>{data.get('TransactionQuantity', 'N/A')}</td>
                <td>{data.get('Kennzeichen', 'N/A')}</td>
            </tr>"""

    # Close the HTML
    html += f"""
        </tbody>
    </table>
    <div class="footer">
        &copy; {current_year} FSV Tankdaten Reader
    </div>
</body>
</html>
"""

    return html

def connect_mqtt():
    """Connect to the MQTT broker."""
    client = mqtt.Client()
    
    # Set up authentication if provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        logger.debug(f"Using MQTT authentication with username: {MQTT_USERNAME}")
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Set up callbacks
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
            # Publish online status
            client.publish(f"{MQTT_TOPIC_PREFIX}/status", "online", retain=True)
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker, return code: {rc}")
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.will_set(f"{MQTT_TOPIC_PREFIX}/status", "offline", retain=True)
    
    try:
        logger.info(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return None

def publish_to_mqtt(client, data_list):
    """Publish data to MQTT topics."""
    if not client:
        logger.warning("MQTT client not connected, skipping publish")
        return
    
    try:
        # Publish last update timestamp
        timestamp = datetime.now().isoformat()
        client.publish(f"{MQTT_TOPIC_PREFIX}/last_update", timestamp)
        logger.debug(f"Published last update timestamp: {timestamp}")
        
        # Publish all transactions as a JSON array
        transactions_json = json.dumps(data_list)
        client.publish(f"{MQTT_TOPIC_PREFIX}/transactions", transactions_json)
        logger.debug(f"Published {len(data_list)} transactions to MQTT")
        
        # Publish individual transactions
        for data in data_list:
            if data and 'TransactionNumber' in data:
                transaction_id = data['TransactionNumber']
                transaction_json = json.dumps(data)
                client.publish(f"{MQTT_TOPIC_PREFIX}/transaction/{transaction_id}", transaction_json)
                logger.debug(f"Published transaction {transaction_id} to MQTT")
        
        # Publish summary statistics
        total_quantity = sum(data.get('RawQuantity', 0) for data in data_list if data)
        client.publish(f"{MQTT_TOPIC_PREFIX}/total_quantity", str(total_quantity))
        
        # Count by article type
        article_counts = {}
        for data in data_list:
            if data and 'RawArticleNumber' in data:
                article = data['RawArticleNumber']
                if article in article_counts:
                    article_counts[article] += 1
                else:
                    article_counts[article] = 1
        
        client.publish(f"{MQTT_TOPIC_PREFIX}/article_counts", json.dumps(article_counts))
        
        logger.info(f"Successfully published all data to MQTT")
    except Exception as e:
        logger.error(f"Error publishing to MQTT: {e}")

def fetch_and_process_data():
    """Fetch and process data from the SFTP server."""
    # Ensure data directory exists
    ensure_directory_exists(DATA_DIR)
    
    # Connect to SFTP
    ssh, sftp = connect_to_sftp()
    if not ssh or not sftp:
        logger.error("Failed to connect to SFTP server, aborting")
        return None
    
    try:
        # Get newest files
        newest_files = get_newest_files(sftp, SFTP_PATH, MAX_FILES)
        
        if not newest_files:
            logger.warning("No XML files found on the server")
            return None
        
        # Download files
        downloaded_files = download_files(sftp, SFTP_PATH, newest_files, DATA_DIR)
        
        # Parse XML files
        data_list = []
        for file_path in downloaded_files:
            data = parse_xml_file(file_path)
            if data:
                data_list.append(data)
        
        # Sort data by transaction date (newest first)
        data_list.sort(
            key=lambda x: x.get('RawDate', '1970-01-01T00:00:00'),
            reverse=True
        )
        
        return data_list
    except Exception as e:
        logger.error(f"An error occurred during data processing: {e}")
        return None
    finally:
        # Close connections
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()
        logger.info("Closed SFTP connection")

def main():
    """Main function to run the script."""
    logger.info("Starting Tank Data Reader")
    
    # Connect to MQTT
    mqtt_client = connect_mqtt()
    
    # Fetch and process data
    data_list = fetch_and_process_data()
    
    if data_list:
        # Generate HTML
        html_content = generate_html(data_list)
        
        # Write HTML to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Successfully generated HTML file: {OUTPUT_FILE}")
        
        # Publish to MQTT
        if mqtt_client:
            publish_to_mqtt(mqtt_client, data_list)
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
    else:
        logger.warning("No data to process")
    
    logger.info("Tank Data Reader completed")

if __name__ == "__main__":
    main()
