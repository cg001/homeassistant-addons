ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Installiere Systemabhängigkeiten
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    openssh \
    curl

# Aktualisiere pip und installiere Python-Abhängigkeiten direkt
RUN pip3 install --upgrade pip && \
    pip3 install --break-system-packages \
    paramiko \
    paho-mqtt \
    beautifulsoup4 \
    flask

# Kopiere Anwendungsdateien
COPY run.sh /run.sh
COPY sftp_sync.sh /sftp_sync.sh
COPY webserver.py /webserver.py
COPY www/ /www/

# Mache Skripte ausführbar
RUN chmod +x /run.sh /sftp_sync.sh

# Entrypoint
CMD [ "/run.sh" ]
