# Python environment setup
.PHONY: setup
setup:
	pip install uv
	uv venv
	uv sync

# Run tests
.PHONY: test
test:
	pytest tests/ -v

# Run linting
.PHONY: lint
lint:
	ruff check .
	ruff format --check .

# Format code
.PHONY: format
format:
	ruff format .
	ruff check --fix .
	isort .

# Run API server
.PHONY: run-api
run-api:
	uvicorn api.app:app --reload

# Run CLI app
.PHONY: run-cli
run-cli:
	python -m scripts.weather.main

# Build Docker image
.PHONY: docker-build
docker-build:
	docker build -t singular-app .

# Run Docker container
.PHONY: docker-run
docker-run:
	docker run -p 8080:8080 singular-app

# Clean up
.PHONY: clean
clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf __pycache__
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  setup        - Set up Python environment with dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  run-api      - Run the API server"
	@echo "  run-cli      - Run the CLI application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  clean        - Clean up temporary files"
