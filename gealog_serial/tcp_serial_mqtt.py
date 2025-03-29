#!/usr/bin/env python

import socket
import xml.etree.ElementTree as ET
import paho.mqtt.client as mqtt
import time
import sys
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Logger erstellen
logger = logging.getLogger(__name__)

# TCP-to-serial converter settings
TCP_HOST = sys.argv[1]
TCP_PORT = int(sys.argv[2])
MQTT_BROKER = sys.argv[3]
MQTT_PORT = int(sys.argv[4])
MQTT_TOPIC_PREFIX = sys.argv[5]
MQTT_USERNAME = sys.argv[6]
MQTT_PASSWORD = sys.argv[7]

# MQTT settings
#TCP_HOST = '192.168.5.144'  # Change this to the hostname or IP address of your TCP-to-serial converter
#TCP_PORT = 4196  # Change this to the port number of your TCP-to-serial converter
#MQTT_BROKER = 'core-mosquitto'  # Change this to your MQTT broker address
#MQTT_PORT = 1883
#MQTT_TOPIC_PREFIX = 'GEALOG'
#MQTT_USERNAME = 'mqtt_loau'
#MQTT_PASSWORD = 'loau_685'

#logger.info(f"TCP-SERIAL: {TCP_HOST}:{TCP_PORT} BROKER: {MQTT_BROKER}:{MQTT_PORT} CREDENTIALS: {MQTT_USERNAME}:{MQTT_PASSWORD} TOPIC: {MQTT_TOPIC_PREFIX}")

# Connect to MQTT broker
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
    else:
        logger.info("Failed to connect to MQTT broker")

client.on_connect = on_connect
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    logger.info("Error connecting to MQTT broker:", e)
    exit(1)


# Read data from TCP socket and publish to MQTT
try:
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_HOST, TCP_PORT))
    logger.info("Connected to TCP-to-serial converter")

    xml_buffer = ''
    last_received_time = time.time()

    while True:
        received_data = tcp_socket.recv(1024).decode('ISO-8859-1').strip()  # Decode the received data using the specified encoding
        if received_data:
            xml_buffer += received_data
            last_received_time = time.time()

            if xml_buffer.startswith('<?xml') and '</data>' in xml_buffer:
                try:
                    root = ET.fromstring(xml_buffer)
                    source = root.attrib['source']
                    for channel in root.findall('channel'):
                        channel_number = channel.attrib['number']
                        channel_name = channel.attrib['name']
                        channel_unit = channel.attrib['unit']
                        value_time = channel.find('value').attrib['time']
                        value_data = channel.find('value').text
                        mqtt_topic = f"{MQTT_TOPIC_PREFIX}/{source}/{channel_name}" 
                        #mqtt_topic =  MQTT_TOPIC_PREFIX + f"{source}/{channel_name}"
                        mqtt_message = f"{value_data}"
                        client.publish(mqtt_topic, mqtt_message)
                        mqtt_topic_unit = f"{MQTT_TOPIC_PREFIX}/{source}/{channel_name}/unit"
                        #mqtt_topic_unit = MQTT_TOPIC_PREFIX + f"{source}/{channel_name}/unit"
                        mqtt_message_unit = f"{channel_unit}"
                        client.publish(mqtt_topic_unit, mqtt_message_unit)
                        #print(mqtt_topic, mqtt_message)
                    xml_buffer = ''
                except Exception as e:
                    print("Error parsing XML data:", e)
                    print("Received XML data:", xml_buffer)
                    # Clear the XML buffer to prevent further parsing attempts
                    xml_buffer = ''
        else:
            # If no data is received for more than 1 second, reset the XML buffer
            if time.time() - last_received_time > 1:
                xml_buffer = ''

except Exception as e:
    logger.info("Error:", e)
finally:
    tcp_socket.close()
    client.disconnect()