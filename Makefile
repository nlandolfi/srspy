precommit:
	make fmt
	make lint
	make types
	make test
build:
	python3 -m build
deploy:
	python3 -m twine upload dist/*
install:
	pip install -e .
fmt:
	python -m black .
lint:
	python -m ruff .
types:
	mypy src
test:
	python tests/01_smoke_test:_records.py
<<<<<<< HEAD
	python tests/02_smoke_test:_basics.py
=======
>>>>>>> main
freeze:
	pip freeze > requirements.txt

.PHONY: setupenv
setupenv:
	python3 -m venv srspy_env
	. srspy_env/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	make install
