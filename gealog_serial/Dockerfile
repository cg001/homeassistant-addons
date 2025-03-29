ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
    py3-pip \
    py3-pyserial \
    py3-paho-mqtt

# Kopiere Add-on Dateien
COPY run.sh /
COPY tcp_serial_mqtt.py /

# Setze Ausfuerungsrechte
RUN chmod +x /run.sh

# Starte das Add-on
CMD [ "/run.sh" ]