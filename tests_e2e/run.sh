#!/usr/bin/env sh

set -ex

cleanup() {
  docker compose rm -fsv vroxy_e2e
}

cleanup

docker compose up -d --wait vroxy_e2e

docker compose run --rm dev pytest tests_e2e

trap cleanup EXIT
