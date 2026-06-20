.PHONY: help all install install-all install-dev test lint format format-check mypy check clean build dist-check run-example run-example-dry coverage coverage-xml

all: check ## Default target - run full CI check

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package with base dependencies
	pip install -e .

install-all: ## Install package with all language dependencies
	pip install -e ".[all]"

install-dev: ## Install package with all extras plus dev dependencies
	pip install -e ".[all,dev]"

test: ## Run unit tests
	python -m unittest discover tests/ -v

lint: ## Run ruff linter
	ruff check strip_comments/ tests/

format: ## Run ruff formatter
	ruff format strip_comments/ tests/

format-check: ## Check formatting without making changes
	ruff format --check strip_comments/ tests/

mypy: ## Run mypy type checker
	mypy strip_comments/ tests/

coverage: ## Run tests with coverage reporting
	coverage run -m unittest discover tests/ -v
	coverage report --show-missing

coverage-xml: ## Generate XML coverage report
	coverage run -m unittest discover tests/ -v
	coverage xml

check: lint format-check mypy test ## Run full CI check (lint + format check + mypy + test)

clean: ## Clean build artifacts and caches
	rm -rf build/ dist/ *.egg-info .ruff_cache .mypy_cache htmlcov/
	rm -f .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

run-example: ## Run CLI on a test fixture
	python -m strip_comments.cli tests/fixtures/python.py

run-example-dry: ## Run CLI in dry-run mode on a test fixture
	python -m strip_comments.cli --dry-run tests/fixtures/python.py

build: clean ## Build sdist and wheel into dist/
	python -m build

dist-check: build ## Build then validate distribution metadata with twine
	python -m twine check dist/*
