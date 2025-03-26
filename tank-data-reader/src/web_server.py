#!/usr/bin/env python3
"""
Web Server for Tank Data Reader Home Assistant Add-on

This script runs a web server that serves the tank data HTML interface
and provides endpoints for reloading data and API access.

Usage:
    python web_server.py
"""

import os
import sys
import subprocess
import time
import json
import logging
from flask import Flask, jsonify, send_from_directory, request
import threading
from pathlib import Path
import tank_data_reader

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
    logger = logging.getLogger('TankDataWebServer')
    logger.setLevel(log_level)
    
    # Reduce logging level for Flask
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    logger.debug(f"Logging initialized at level: {log_level_str}")
    return logger

logger = setup_logging()

# Get configuration from environment variables
PORT = int(os.environ.get('PORT', '8000'))
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', '300'))

# Local Configuration
WWW_DIR = '/app/www'
HTML_FILE = 'index.html'

# Create Flask app
app = Flask(__name__)

# Create a lock for thread safety
data_lock = threading.Lock()

# Store the last update time
last_update_time = time.time() - UPDATE_INTERVAL  # Initialize to trigger immediate update

def ensure_www_directory():
    """Ensure that the www directory exists."""
    Path(WWW_DIR).mkdir(parents=True, exist_ok=True)
    # Create a default index.html if it doesn't exist
    index_path = Path(WWW_DIR) / HTML_FILE
    if not index_path.exists():
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>Tank Data Reader</h1><p>Loading data...</p></body></html>")
        logger.info(f"Created default {HTML_FILE}")

def update_data():
    """Update the data from the SFTP server."""
    global last_update_time
    
    with data_lock:
        # Run the tank_data_reader module
        logger.info("Updating data from SFTP server...")
        try:
            # Call the main function directly
            tank_data_reader.main()
            last_update_time = time.time()
            logger.info("Data updated successfully")
            return True, "Data updated successfully"
        except Exception as e:
            logger.error(f"Error updating data: {e}")
            return False, f"Error updating data: {e}"

def scheduled_update():
    """Run scheduled updates at the specified interval."""
    while True:
        time_since_last_update = time.time() - last_update_time
        if time_since_last_update >= UPDATE_INTERVAL:
            logger.info(f"Running scheduled update (last update was {time_since_last_update:.1f} seconds ago)")
            update_data()
        else:
            logger.debug(f"Skipping scheduled update (last update was {time_since_last_update:.1f} seconds ago)")
        
        # Sleep for a shorter time to be more responsive
        time.sleep(min(60, UPDATE_INTERVAL / 10))

@app.route('/')
def index():
    """Serve the index.html file."""
    return send_from_directory(WWW_DIR, HTML_FILE)

@app.route('/<path:path>')
def static_files(path):
    """Serve static files from the www directory."""
    return send_from_directory(WWW_DIR, path)

@app.route('/reload')
def reload_data():
    """Reload the data from the SFTP server."""
    success, message = update_data()
    
    response = {
        'success': success,
        'message': message,
        'timestamp': time.strftime('%d.%m.%Y, %H:%M:%S')
    }
    return jsonify(response)

@app.route('/api/status')
def api_status():
    """Return the status of the add-on."""
    return jsonify({
        'status': 'online',
        'last_update': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(last_update_time)),
        'update_interval': UPDATE_INTERVAL,
        'next_update': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(last_update_time + UPDATE_INTERVAL))
    })

@app.route('/api/tankdata')
def api_tankdata():
    """Return the tank data as JSON."""
    try:
        # Read the data from the tank_data_reader module
        data_list = tank_data_reader.fetch_and_process_data()
        if data_list:
            return jsonify({
                'success': True,
                'data': data_list,
                'count': len(data_list),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            })
    except Exception as e:
        logger.error(f"Error retrieving tank data: {e}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving tank data: {e}",
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
        })

def run_server():
    """Run the web server."""
    # Ensure the www directory exists
    ensure_www_directory()
    
    # Run an initial update
    update_data()
    
    # Start the scheduled update thread
    update_thread = threading.Thread(target=scheduled_update, daemon=True)
    update_thread.start()
    
    # Start the Flask server
    logger.info(f"Starting web server on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    run_server()
