#!/bin/sh
set -x
echo "Running entry point"
echo $@
## Run nginxi Web Server
/usr/sbin/nginx -c /etc/nginx/nginx.conf

# Execute arguments
echo >&2 $0: Continuing with "$@"...
exec "$@"
