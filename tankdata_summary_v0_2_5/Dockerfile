ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

RUN apk add --no-cache python3 py3-pip openssh
RUN pip3 install --break-system-packages flask paramiko

COPY rootfs/ /
COPY src/ /app/
COPY www/ /app/www/

RUN chmod +x /etc/services.d/test/run
WORKDIR /app