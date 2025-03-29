#!/usr/bin/with-contenv bashio
set -e

SERIAL_IP=$(bashio::config 'serial_ip')
SERIAL_PORT=$(bashio::config 'serial_port')
MQTT_BROKER=$(bashio::config 'mqtt_broker')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_TOPIC=$(bashio::config 'mqtt_topic')
MQTT_USERNAME=$(bashio::config 'mqtt_username')
MQTT_PASSWORD=$(bashio::config 'mqtt_password')

#SERIAL_IP=192.168.5.144
#SERIAL_PORT=4196
#MQTT_BROKER=core-mosquitto
#MQTT_PORT=1883
#MQTT_TOPIC=GEALOG
#MQTT_USERNAME=mqtt_loau
#MQTT_PASSWORD=loau_685

bashio::log.info "TCP Serial: $SERIAL_IP:$SERIAL_PORT MQTT: $MQTT_BROKER:$MQTT_PORT TOPIC:$MQTT_TOPIC"

# Starte das Python-Skript mit den Konfigurationsoptionen
python3 /tcp_serial_mqtt.py "$SERIAL_IP" "$SERIAL_PORT" "$MQTT_BROKER" "$MQTT_PORT" "$MQTT_TOPIC" "$MQTT_USERNAME" "$MQTT_PASSWORD"