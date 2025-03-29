ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache nginx apache2-utils

COPY rootfs/ /

# Keine CMD, s6-overlay übernimmt Prozessstart
