#!/bin/bash

HOST=$(bashio::config 'sftp_host')
PORT=$(bashio::config 'sftp_port')
USER=$(bashio::config 'sftp_username')
PASS=$(bashio::config 'sftp_password')
REMOTE_PATH=$(bashio::config 'sftp_path')
TOPIC_PREFIX=$(bashio::config 'mqtt_topic_prefix')
MQTT_HOST=$(bashio::config 'mqtt_host')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USER=$(bashio::config 'mqtt_username')
MQTT_PASS=$(bashio::config 'mqtt_password')

mkdir -p /tmp/tank_data
lftp -u $USER,$PASS sftp://$HOST:$PORT <<EOF
cd $REMOTE_PATH
mget *.json -o /tmp/tank_data/
bye
EOF

# Publiziere zu MQTT
for file in /tmp/tank_data/*.json; do
  [ -e "$file" ] || continue
  id=$(basename "$file" .json)
  cat "$file" | mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -u "$MQTT_USER" -P "$MQTT_PASS" -t "$TOPIC_PREFIX/transaction/$id" -s
done
