.PHONY: help install dev test lint format typecheck build clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install .

dev:  ## Install in development mode with all extras
	pip install -e ".[dev,images,ai-images]"

test:  ## Run tests
	python -m pytest tests/ -q

test-cov:  ## Run tests with coverage
	python -m pytest tests/ --cov=pptx_designer --cov-report=html --cov-report=term

lint:  ## Run linter
	python -m ruff check src/

format:  ## Format code
	python -m ruff format src/
	python -m ruff check src/ --fix

typecheck:  ## Run type checker
	python -m mypy src/pptx_designer/

build:  ## Build sdist and wheel
	python -m build

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

release:  ## Create a release (usage: make release v1.0.0)
	@echo "Usage: make release v1.0.0"
	@echo "This will tag and push to trigger CI release."
	git tag -a $(v) -m "Release $(v)"
	git push origin $(v)
