#!/usr/bin/env sh

set -e

if [ "$CI" != "true" ]; then
    echo "Cowardly refusing to run bootstrap on what looks like a non-CI environment."
    echo "This bootstrap is only intended for ephemeral CI machines."
    echo "Running this on a real machine will make it insecure."
    exit 1
fi

set -x

apt-get update

apt-get install -y --no-install-recommends \
    ca-certificates \
    cron \
    curl \
    git \
    procps

curl -o /usr/local/share/ca-certificates/pebble.minica.crt https://raw.githubusercontent.com/letsencrypt/pebble/main/test/certs/pebble.minica.pem

update-ca-certificates