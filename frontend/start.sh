#!/bin/sh
# Default to 80 if PORT not set
PORT=${PORT:-80}
echo "Starting nginx on port $PORT"
# Substitute PORT in nginx config
envsubst '$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
cat /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
