# Makefile for 2ª Vara Cível de Cariacica
# Poetry-enhanced development workflow automation

.PHONY: help install dev test lint format security clean deploy docs

# Default target
help:
	@echo "🏛️ 2ª Vara Cível de Cariacica - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install     Install all dependencies"
	@echo "  dev-setup   Complete development environment setup"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev         Start development server"
	@echo "  prod        Start production server"
	@echo "  shell       Open Poetry shell"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  test        Run complete test suite"
	@echo "  test-unit   Run unit tests only"
	@echo "  test-int    Run integration tests only"
	@echo "  lint        Run all linting checks"
	@echo "  format      Format code with Black and isort"
	@echo "  security    Run security audit"
	@echo "  quality     Complete quality assessment"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-init     Initialize database tables"
	@echo "  db-reset    Reset database (development)"
	@echo ""
	@echo "Deployment:"
	@echo "  build       Build application for deployment"
	@echo "  deploy      Deploy to production"
	@echo ""
	@echo "Documentation:"
	@echo "  docs        Generate documentation"
	@echo "  docs-serve  Serve documentation locally"

# Installation and Setup
install:
	@echo "📦 Installing dependencies..."
	poetry install --with dev,test,monitoring

dev-setup:
	@echo "🔧 Setting up development environment..."
	poetry run python scripts/dev-setup.py

# Development Commands
dev:
	@echo "🚀 Starting development server..."
	poetry run python main.py

prod:
	@echo "🌐 Starting production server..."
	poetry run python main_optimized_final.py

shell:
	@echo "🐚 Opening Poetry shell..."
	poetry shell

# Testing
test:
	@echo "🧪 Running complete test suite..."
	poetry run pytest --cov=. --cov-report=term-missing --cov-report=html

test-unit:
	@echo "🔬 Running unit tests..."
	poetry run pytest tests/unit/ -v

test-int:
	@echo "🔗 Running integration tests..."
	poetry run pytest tests/integration/ -v

test-security:
	@echo "🛡️ Running security tests..."
	poetry run pytest tests/security/ -v

test-accessibility:
	@echo "♿ Running accessibility tests..."
	poetry run pytest tests/accessibility/ -v

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	poetry run flake8 .
	poetry run mypy .

format:
	@echo "🎨 Formatting code..."
	poetry run black .
	poetry run isort .

format-check:
	@echo "📋 Checking code formatting..."
	poetry run black --check .
	poetry run isort --check-only .

security:
	@echo "🔒 Running security audit..."
	poetry run bandit -r . -f json
	poetry run safety check

quality:
	@echo "📊 Running complete quality assessment..."
	poetry run python scripts/quality-check.py

# Pre-commit
pre-commit-install:
	@echo "🪝 Installing pre-commit hooks..."
	poetry run pre-commit install

pre-commit-run:
	@echo "🪝 Running pre-commit on all files..."
	poetry run pre-commit run --all-files

# Database Operations
db-init:
	@echo "🗄️ Initializing database..."
	poetry run python -c "from app import create_app; from database import db; app = create_app(); app.app_context().push(); db.create_all()"

db-reset:
	@echo "🔄 Resetting database..."
	poetry run python -c "from app import create_app; from database import db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Build and Deployment
build:
	@echo "🏗️ Building application..."
	poetry build

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

deploy:
	@echo "🚀 Deploying to production..."
	@echo "Run 'poetry run court-prod' for production deployment"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	poetry run sphinx-build -b html docs/ docs/_build/

docs-serve:
	@echo "📖 Serving documentation locally..."
	poetry run python -m http.server 8000 --directory docs/_build/

# Health Checks
health:
	@echo "🏥 Running health checks..."
	poetry run python -c "from app import create_app; app = create_app(); print('✅ Application can be created successfully')"

check-deps:
	@echo "📋 Checking dependencies..."
	poetry check
	poetry show --outdated

# Performance
perf-test:
	@echo "⚡ Running performance tests..."
	poetry run python -c "import time; from app import create_app; start=time.time(); app=create_app(); print(f'App startup: {(time.time()-start)*1000:.2f}ms')"

# Monitoring
logs:
	@echo "📊 Viewing application logs..."
	tail -f app.log

# Complete workflow commands
ci:
	@echo "🔄 Running CI pipeline..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test

release:
	@echo "🎉 Preparing release..."
	$(MAKE) quality
	$(MAKE) build
	@echo "✅ Release ready for deployment"