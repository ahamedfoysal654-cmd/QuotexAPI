.PHONY: help install install-dev test coverage lint format clean

help:
	@echo "QuotexAPI - Makefile commands"
	@echo ""
	@echo "install          Install package in production mode"
	@echo "install-dev      Install package with development dependencies"
	@echo "test             Run tests"
	@echo "coverage         Run tests with coverage report"
	@echo "lint             Run linting (flake8, mypy)"
	@echo "format           Format code (black, isort)"
	@echo "clean            Clean up build artifacts"
	@echo "run-example      Run basic usage example"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

coverage:
	pytest --cov=QuotexAPI --cov-report=html --cov-report=term

lint:
	flake8 QuotexAPI/
	mypy QuotexAPI/

format:
	black QuotexAPI/ tests/ examples/
	isort QuotexAPI/ tests/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-example:
	python examples/basic_usage.py
