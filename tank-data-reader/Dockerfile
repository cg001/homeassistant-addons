ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

COPY rootfs /
COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
