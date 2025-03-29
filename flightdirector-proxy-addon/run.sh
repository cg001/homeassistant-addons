#!/usr/bin/with-contenv bashio

# Erstelle erforderliche Ordner
mkdir -p /run/nginx

# Starte nginx im Vordergrund (damit er als PID 1 läuft)
exec nginx -g 'daemon off;'
