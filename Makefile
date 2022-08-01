DEV=docker-compose run dev

default: requirements.txt
	docker-compose build vroxy dev

requirements.txt: requirements.in
	$(DEV) pip-compile $<

.PHONY: test
test:
	$(DEV) pytest

.PHONY: sh
sh:
	$(DEV) bash