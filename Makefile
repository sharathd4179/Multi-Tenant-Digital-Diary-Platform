.PHONY: help install install-dev test lint format clean docker-build docker-up docker-down migrate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v --cov=backend.app --cov-report=term

lint: ## Run linters
	flake8 backend/ frontend/ --max-line-length=120
	mypy backend/app --ignore-missing-imports
	black --check backend/ frontend/
	isort --check backend/ frontend/

format: ## Format code
	black backend/ frontend/
	isort backend/ frontend/

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

docker-build: ## Build Docker images
	cd infrastructure/docker && docker-compose build

docker-up: ## Start Docker containers
	cd infrastructure/docker && docker-compose up -d

docker-down: ## Stop Docker containers
	cd infrastructure/docker && docker-compose down

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(message)"

seed: ## Seed database with demo data
	python scripts/seed_demo_data.py

index: ## Build FAISS indexes
	python scripts/create_faiss_index.py

