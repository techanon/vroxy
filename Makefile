DEV=docker compose run --rm dev

default: requirements.txt
	docker compose build vroxy dev

requirements.txt: requirements.in
	$(DEV) pip-compile $<

.PHONY: test
test:
	$(DEV) pytest

.PHONY: test-e2e
test-e2e:
	./tests_e2e/run.sh

.PHONY: lint
lint: flake8

.PHONY: flake8
flake8:
	$(DEV) flake8

.PHONY: sh
sh:
	$(DEV) bash