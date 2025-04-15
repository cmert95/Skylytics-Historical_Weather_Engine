# ⛈️ Weather Forecast Data Pipeline

This is a modular and automated ETL pipeline designed to collect, clean, and store weather forecast data based on the user's IP location. The system is built with Dockerized steps and is fully integrated into a Jenkins CI workflow, including unit testing, test coverage tracking, and ready for future improvements.

## Project Overview

### 🧩 1. Modular Scripts
Each step of the ETL process — IP detection, weather fetch, and data cleaning — is handled by a dedicated Python script for clarity and maintainability.

### 🐳 2. Dockerized Execution
All components, including tests, run in isolated Docker containers managed with Docker Compose.

### ⚙️ 3. Jenkins CI Pipeline
A Jenkins pipeline automates the workflow with scheduled execution, test runs, and coverage tracking.

### 🌐 4. GitHub Integration
CI can be triggered via GitHub pushes (via manual trigger or webhook). The project follows Git best practices and supports feature-based branching.

### 📦 5. Clean Outputs
Processed weather data is saved in both `.csv` and `.parquet` formats — ready for analysis or visualization tools.

## Technologies Used

- **Python**: `requests`, `pandas`, `pytest`, `logging`
- **Docker**: Containerization of each ETL and testing step
- **Docker Compose**: For all services and test environments
- **Jenkins**: CI pipeline with daily schedule, test runner, logging, and coverage
- **GitHub**: Version control and CI integration with Jenkins
- **Pre-commit**: `black`, `flake8`, and formatting tools for cleaner commits
- **pytest + coverage**: Unit + edge-case testing with real-time coverage stats
- **APIs**: IP and weather data source


## ✅ Test Coverage

![coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)
- Coverage is calculated using `pytest-cov`
- Results are logged both locally and inside Jenkins

---

## Running Locally (ETL + Tests)

```bash
# Step-by-step ETL
docker compose run --rm ip
docker compose run --rm weather
docker compose run --rm -e INTERVAL=30min cleaning

# Run all tests with coverage
docker compose run --rm test
```

> 📝 Make sure `.env` file exists with your `API_KEY`.

## Jenkins Pipeline

The `Jenkinsfile` includes:

- Cleanup of old logs and data
- Environment file checks
- Full ETL pipeline run
- Unit tests with coverage
- Dynamic parameter injection (e.g., INTERVAL)
- Daily 08:30 AM run (Mon–Fri)

---

### 🗺️  Planned or In Progress

1. **CD (Continuous Delivery)** to a database or cloud destination
2. **Power BI** or **Tableau** dashboards

---
I built this project to show how I like to build things.
