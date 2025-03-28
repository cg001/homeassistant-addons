#!/usr/bin/with-contenv bashio

# Aktiviere Python venv
source /venv/bin/activate

# Starte Webserver im Hintergrund
python3 /webserver.py &

# Wiederhole alle x Sekunden
while true; do
    bash /sftp_sync.sh
    sleep $(bashio::config 'update_interval')
done
