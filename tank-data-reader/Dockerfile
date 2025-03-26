ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system packages needed for building Python packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-wheel \
    py3-setuptools \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    make \
    git \
    curl

# Upgrade pip and setuptools and prefer pre-built binaries
RUN pip3 install --upgrade pip setuptools wheel

# Install cryptography first from binary wheel to avoid build issues
RUN pip3 install --only-binary cryptography cryptography

# Install other Python dependencies
RUN pip3 install --no-cache-dir \
    paramiko \
    paho-mqtt \
    beautifulsoup4 \
    flask

# Copy root filesystem
COPY rootfs /

# Copy source code
COPY src /app
COPY www /app/www

# Set working directory
WORKDIR /app

# Copy run script
COPY run.sh /
RUN chmod +x /run.sh

# Make healthcheck script executable
RUN chmod +x /usr/bin/healthcheck

# Set up healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /usr/bin/healthcheck

# Set entrypoint
ENTRYPOINT ["/run.sh"]

# Labels for Home Assistant
LABEL \
    io.hass.name="Tank Data Reader" \
    io.hass.description="Reads tank transaction data from SFTP server and publishes to MQTT" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    maintainer="Christian Graf <cg@ceeqoo.com>"