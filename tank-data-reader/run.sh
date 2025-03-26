#!/usr/bin/with-contenv bashio

# Get config
SFTP_HOST=$(bashio::config 'sftp_host')
SFTP_PORT=$(bashio::config 'sftp_port')
SFTP_USERNAME=$(bashio::config 'sftp_username')
SFTP_PASSWORD=$(bashio::config 'sftp_password')
SFTP_PATH=$(bashio::config 'sftp_path')
MQTT_HOST=$(bashio::config 'mqtt_host')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USERNAME=$(bashio::config 'mqtt_username')
MQTT_PASSWORD=$(bashio::config 'mqtt_password')
MQTT_TOPIC_PREFIX=$(bashio::config 'mqtt_topic_prefix')
UPDATE_INTERVAL=$(bashio::config 'update_interval')
LOG_LEVEL=$(bashio::config 'log_level')

# Export as environment variables
export SFTP_HOST
export SFTP_PORT
export SFTP_USERNAME
export SFTP_PASSWORD
export SFTP_PATH
export MQTT_HOST
export MQTT_PORT
export MQTT_USERNAME
export MQTT_PASSWORD
export MQTT_TOPIC_PREFIX
export UPDATE_INTERVAL
export LOG_LEVEL

# Welcome message
bashio::log.info "Starting Tank Data Reader add-on"
bashio::log.info "SFTP Server: ${SFTP_HOST}:${SFTP_PORT}"
bashio::log.info "MQTT Broker: ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Update interval: ${UPDATE_INTERVAL} seconds"
bashio::log.info "Log level: ${LOG_LEVEL}"

# Create data directory if it doesn't exist
mkdir -p /data/tank_data

# Start the web server
cd /app
python3 web_server.py
