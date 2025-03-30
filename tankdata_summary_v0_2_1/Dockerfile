
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

RUN apk add --no-cache python3 py3-pip py3-flask
COPY . /app
WORKDIR /app

CMD ["python3", "server.py"]
