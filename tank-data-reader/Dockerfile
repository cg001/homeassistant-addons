ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-wheel \
    py3-setuptools \
    git

# Install Python dependencies
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
RUN chmod a+x /run.sh

# Set entrypoint
ENTRYPOINT ["/run.sh"]

# Labels
LABEL \
    io.hass.name="Tank Data Reader" \
    io.hass.description="Reads tank transaction data from SFTP server and publishes to MQTT" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    maintainer="Christian Graf <cg@ceeqoo.com>"
