#!/usr/bin/with-contenv bashio

mkdir -p /run/nginx
nginx

while true; do
  bash /fetch_and_publish.sh
  sleep $(bashio::config 'update_interval')
done
