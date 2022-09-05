#!/usr/bin/env sh

set -ex

cleanup() {
  docker compose rm -fsv pebble vroxy-install-e2e.test
}

cleanup

# trap cleanup EXIT

docker compose up -d --wait pebble
docker compose up -d vroxy-install-e2e.test

DRUN="docker compose exec vroxy-install-e2e.test"

$DRUN ./tests_e2e/test_deb_bootstrap.sh
$DRUN ./vroxy_install_deb.sh
sleep 15
# test tmux session
echo "## Testing tmux session"
$DRUN curl -f http://localhost:8420/healthz
echo
# test nginx
echo "## Testing nginx"
$DRUN curl -f -H 'Host: vroxy-install-e2e.test' -k https://localhost/healthz
echo