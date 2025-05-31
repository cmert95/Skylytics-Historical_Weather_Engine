.PHONY: \
  help \
  run \
  test test-unit test-integration testcov coverage-html \
  ip weather cleaning \
  build-app build-test \
  cleanall cleantemp cleandata cleanlogs \
  lint format \
  dockerrebuild clean-docker

# ---------------------------------------------------
# Help
# ---------------------------------------------------
help:  ## Show available commands
	@echo "🛠️  Available commands:"
	@awk -F':.*?## ' '/^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' Makefile

# ---------------------------------------------------
# Full pipeline
# ---------------------------------------------------
run: ## Run the full ETL pipeline
	@echo "🚀 Running full ETL pipeline..."
	docker compose run --rm app

# ---------------------------------------------------
# Testing
# ---------------------------------------------------
test: ## Run all tests (unit + integration, local)
	@echo "🧪 Running ALL tests locally..."
	poetry run pytest

test-unit: ## Run only unit tests (via Docker)
	@echo "🧪 Running UNIT tests in Docker..."
	docker compose run --rm -e TEST_TYPE=unit test

test-integration: ## Run only integration tests (via Docker)
	@echo "🧪 Running INTEGRATION tests in Docker..."
	docker compose run --rm -e TEST_TYPE=integration test

testcov: ## Run all tests with coverage (unit + integration)
	@echo "🧪 Running tests with coverage..."
	docker compose run --rm test poetry run pytest --cov=src --cov-report=term-missing

coverage-html: ## Generate test coverage report in HTML format
	@echo "🧪 Generating coverage report in HTML format..."
	mkdir -p htmlcov
	docker compose run --rm test poetry run pytest --cov=src --cov-report=html
	@echo "📂 HTML report generated at: htmlcov/index.html"

# ---------------------------------------------------
# ETL Steps (as individual containers)
# ---------------------------------------------------
ip: ## Run Step1: IP detection step
	@echo "🌍 Running Step 1: IP detection..."
	docker compose run --rm location_resolver

weather: ## Run Step2: Fetch weather data
	@echo "⛅ Running Step 2: Fetching weather data..."
	docker compose run --rm weather_data_fetcher

cleaning: ## Run Step3: Clean and transform weather data
	@echo "🧹 Running Step 3: Cleaning and transforming data..."
	docker compose run --rm data_cleaner

# ---------------------------------------------------
# Build individual Docker images
# ---------------------------------------------------
build-app: ## Rebuild app image only
	@echo "🐳 Building app image..."
	docker compose build app

build-test: ## Rebuild test image only
	@echo "🐳 Building test image..."
	docker compose build test

# ---------------------------------------------------
# Cleaning utilities
# ---------------------------------------------------
cleanall: ## Remove raw/cleaned data, logs and config files
	@echo "🧹 Cleaning all data, logs, and config files..."
	find data/sources -name '*.json' -delete
	find data/staging -name '*.csv' -delete
	find logs -name '*.log' -delete

cleantemp: ## Remove raw data and logs
	@echo "🗑️  Cleaning raw data and logs..."
	find data/sources -name '*.json' -delete
	find logs -name '*.log' -delete

cleandata: ## Remove data files
	@echo "📦 Cleaning raw and cleaned data..."
	find data/sources -name '*.json' -delete
	find data/staging -name '*.csv' -delete

cleanlogs: ## Remove log files
	@echo "📄 Cleaning logs..."
	find logs -name '*.log' -delete

# ---------------------------------------------------
# Code Quality
# ---------------------------------------------------
lint: ## Check code style with black & ruff
	@echo "🔍 Linting code with black + ruff..."
	black --check src/ tests/
	ruff check src/ tests/

format: ## Format code with black & ruff
	@echo "🧼 Formatting code with black + ruff..."
	black src/ tests/
	ruff --fix src/ tests/

# ---------------------------------------------------
# Docker
# ---------------------------------------------------
dockerrebuild: ## Rebuild Docker images
	@echo "🐳 Rebuilding Docker images..."
	docker compose build --no-cache

clean-docker: ## Remove dangling Docker containers/images/volumes
	@echo "🗑️ Cleaning up Docker junk..."
	docker container prune -f
	docker image prune -f
	docker volume prune -f
