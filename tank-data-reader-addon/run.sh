#!/usr/bin/with-contenv bashio

# Starte Webserver & Sync im Hintergrund
python3 /webserver.py &

while true; do
    bash /sftp_sync.sh
    sleep $(bashio::config 'update_interval')
done
