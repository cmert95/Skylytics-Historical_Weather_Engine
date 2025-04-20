.PHONY: \
  help \
  ip weather cleaning cleaning20 cleaning15 runall \
  cleanall cleantemp cleandata cleanlogs cleanconfig \
  test testcov \
  lint format \
  dockerrebuild

help:  ## Show available commands
	@echo "🛠️  Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

ip: ## Run Step1: IP detection step
	@echo "🌍 Running Step 1: IP detection..."
	docker compose run --rm ip

weather: ## Run Step2: Fetch weather data
	@echo "⛅ Running Step 2: Fetching weather data..."
	docker compose run --rm weather

cleaning: ## Run Step3: Clean and transform weather data (default 30min)
	@echo "🧹 Running Step 3: Cleaning and transforming data (default 30min)..."
	docker compose run --rm -e INTERVAL=30min cleaning

cleaning20: ## Run cleaning step with 20min interval
	@echo "🧹 Cleaning data with 20min interval..."
	docker compose run --rm -e INTERVAL=20min cleaning

cleaning15: ## Run cleaning step with 15min interval
	@echo "🧹 Cleaning data with 15min interval..."
	docker compose run --rm -e INTERVAL=15min cleaning

test: ## Run all tests without coverage
	@echo "🧪 Running tests (without coverage)..."
	pytest

testcov: ## Run all tests with coverage
	@echo "🧪 Running tests with coverage..."
	docker compose run --rm test

runall: ## Run the full ETL pipeline
	@echo "🚀 Running full ETL pipeline..."
	docker compose run --rm ip
	docker compose run --rm weather
	docker compose run --rm -e INTERVAL=30min cleaning

cleanall: ## Remove raw/cleaned data, logs and config files
	@echo "🧹 Cleaning all data, logs, and config files..."
	rm -f data/raw/*.json
	rm -f data/cleaned/*.csv
	rm -f data/cleaned/*.parquet
	rm -f logs/*.log
	rm -f config/*.json

cleantemp: ## Remove raw data, logs and config files
	@echo "🗑️  Cleaning raw data, logs, and config..."
	rm -f data/raw/*.json
	rm -f logs/*.log
	rm -f config/*.json

cleandata: ## Remove data files
	@echo "📦 Cleaning raw and cleaned data..."
	rm -f data/raw/*.json
	rm -f data/cleaned/*.csv
	rm -f data/cleaned/*.parquet

cleanlogs: ## Remove log files
	@echo "📄 Cleaning logs..."
	rm -f logs/*.log

cleanconfig: ## Remove config files
	@echo "⚙️  Cleaning config files..."
	rm -f config/*.json

dockerrebuild: ## Rebuild all Docker images
	@echo "🐳 Rebuilding Docker images..."
	docker compose build --no-cache

lint: ## Run black, flake8 and isort in check mode
	@echo "🔍 Linting code with black, flake8, and isort..."
	black --check src/ tests/
	flake8 src/ tests/
	isort --check-only src/ tests/

format: ## Auto-format code with black and isort
	@echo "🧼 Auto-formatting code with black and isort..."
	black src/ tests/
	isort src/ tests/
