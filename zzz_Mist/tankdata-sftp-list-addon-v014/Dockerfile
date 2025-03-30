ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip openssh
RUN pip3 install --break-system-packages paramiko

COPY rootfs/ /
COPY src/ /app/

RUN chmod +x /etc/services.d/test/run

WORKDIR /app
