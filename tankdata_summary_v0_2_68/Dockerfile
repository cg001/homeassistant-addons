ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

# Installiere Python, pip, SSH und NGINX
RUN apk add --no-cache \
    python3 \
    py3-pip \
    openssh \
    nginx

# Installiere Python-Pakete
RUN pip3 install --break-system-packages flask paramiko

# Kopiere Dateien
COPY rootfs/ /
COPY src/ /app/
COPY www/ /app/www/
COPY nginx.conf /etc/nginx/nginx.conf

# Setze Berechtigungen für die run-Datei
RUN chmod +x /etc/services.d/test/run

WORKDIR /app