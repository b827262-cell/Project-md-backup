.PHONY: install lint typecheck test build migrate check

install:
	python -m pip install -e '.[dev]'

lint:
	ruff check backend database tests

typecheck:
	mypy backend database

test:
	pytest

build:
	npm --prefix frontend run build

migrate:
	python database/migrate.py

check: lint typecheck test build
