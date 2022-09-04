DEV=docker compose run --rm dev

default: requirements.txt
	docker compose build vroxy dev

requirements.txt: requirements.in
	$(DEV) pip-compile $<

.PHONY: test
test:
	$(DEV) pytest --cov --cov-report=html --cov-report=xml

.PHONY: test-e2e
test-e2e:
	./tests_e2e/run.sh

.PHONY: sh
sh:
	$(DEV) bash