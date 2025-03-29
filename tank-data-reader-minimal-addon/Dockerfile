ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache openssh-client mosquitto-clients bash nginx curl lftp

COPY run.sh /run.sh
COPY fetch_and_publish.sh /fetch_and_publish.sh
COPY www/ /www/

RUN chmod +x /run.sh /fetch_and_publish.sh

CMD ["/run.sh"]
