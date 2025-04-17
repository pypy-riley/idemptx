.PHONY: install test test-cov lint format build publish clean

install:
	poetry install

test:
	poetry run pytest tests/

test-cov:
	poetry run pytest --cov=idemptx tests/

lint:
	poetry run ruff check src tests

format:
	poetry run ruff format src tests

build:
	poetry build

publish: build
	poetry publish

clean:
	rm -rf dist .pytest_cache .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
