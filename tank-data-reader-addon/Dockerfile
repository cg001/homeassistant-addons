ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    python3 \
    py3-pip \
    openssh \
    bash

COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt

COPY run.sh /run.sh
COPY sftp_sync.sh /sftp_sync.sh
COPY webserver.py /webserver.py
COPY www/ /www/

RUN chmod +x /run.sh /sftp_sync.sh

CMD [ "/run.sh" ]
