# Modular Automated ETL Pipeline
⛅ *Powered by weather forecast data*

This is a fully modular and automated ETL pipeline designed to collect, clean, and store weather forecast data based on the user's IP location. The system is built with Dockerized steps and is fully integrated into a Jenkins CI workflow, including unit testing, test coverage tracking, and ready for future improvements.


## 🪄 Technologies and Tools Used

- **Python**: `requests`, `pandas`, `pytest`, `logging`
- **Docker**: Containerization of each ETL and testing step
- **Docker Compose**: For all services and test environments
- **Jenkins**: CI pipeline with daily schedule, test runner, logging, and coverage
- **GitHub**: Version control and CI integration with Jenkins
- **Pre-commit**: `black` and `ruff` for formatting and linting
- **pytest + coverage**: Unit + edge-case testing with real-time coverage stats
- **Makefile**: Provides simplified commands to run ETL steps, tests, and formatting
- **APIs**: IP and weather data source


## ✅ Test Coverage

![coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)
- Test coverage is measured using `pytest` and `pytest-cov`.
- Run `make testcov` to see a detailed coverage report in the terminal.

---

## 📦 Makefile Commands

You can use `make` commands to run pipeline steps, clean files, run tests, and format code.

To see all available commands:

```bash
make help
```

## ⛓️ Running Locally (ETL + Tests)

If you don't want to use the Makefile, you can still run each step manually using Docker Compose:

```bash
# Step-by-step ETL
docker compose run --rm ip
docker compose run --rm weather
docker compose run --rm -e INTERVAL=30min cleaning

# Run all tests with coverage
docker compose run --rm test
```
---
> 📝 Make sure `.env` file exists with your `API_KEY`.

## 🤵🏻 Jenkins Pipeline

The `Jenkinsfile` includes:

- Cleanup of old logs and data
- Environment file checks
- Test container image build
- Full ETL pipeline run
- Unit tests with coverage
- Dynamic parameter injection
- Pre/post directory check
- Scheduled daily execution

---

### 🧳  Planned or In Progress

1. **Automated data delivery** to a PostgreSQL database
2. **Power BI** or **Tableau** dashboards

---
I built this project to show how I like to build things.
