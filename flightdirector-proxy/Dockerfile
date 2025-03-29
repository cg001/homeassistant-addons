ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

RUN apk add --no-cache nginx bash python3 py3-pip curl
RUN pip3 install flask requests

COPY rootfs/ /
COPY src/ /app/

RUN chmod +x /etc/services.d/nginx/run /etc/services.d/nginx/finish

WORKDIR /app
