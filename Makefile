.PHONY: help setup install test lint format run docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  setup          - Setup development environment"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  run            - Run development server"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start Docker containers"
	@echo "  docker-down    - Stop Docker containers"
	@echo "  clean          - Clean cache and temp files"

setup:
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Environment ready. Activate with: source venv/bin/activate"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src/ --cov-report=html

lint:
	ruff check .
	mypy src/

format:
	black .
	ruff check --fix .

run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "Services started."
	@echo "API: http://localhost:8000"
	@echo "Dashboard: http://localhost:8501"
	@echo "API Docs: http://localhost:8000/docs"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov .coverage