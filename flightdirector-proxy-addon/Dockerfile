ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache nginx apache2-utils

COPY rootfs/ /

# Set correct permissions for s6-overlay
RUN chmod +x /etc/services.d/nginx/run /etc/services.d/nginx/finish
