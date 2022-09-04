#!/usr/bin/env sh

set -ex

cleanup() {
  docker compose rm -fsv vroxy_e2e vroxy_e2e_authz
}

cleanup

docker compose up -d --wait vroxy_e2e vroxy_e2e_authz

docker compose run --rm dev pytest tests_e2e

trap cleanup EXIT
