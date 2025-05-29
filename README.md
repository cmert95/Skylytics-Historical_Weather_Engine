# 🌦️ Skylytics – AI Forecasts vs Reality
📍 *Building a localized air-weather dataset and benchmarking ML/DL models against real-world forecasts*

This project focuses on generating a localized, time-series dataset of historical weather data for a specific region, and using it to explore the predictive capabilities of modern machine learning and deep learning models.

Along the way, the project serves as a complete data engineering + modeling workflow:
- 🔁 Full ETL pipeline for 10+ years of localized weather data
- 🔮 Daily predictions with ML/DL models
- ⚖️ Accuracy comparisons against real weather forecast services
- 📊 Visualization of prediction errors, model drift, and performance patterns

Ultimately, this project seeks to answer:
> “How close can open-source ML models get to the accuracy of professional forecasting systems?”

## 📌 Project Highlights

### Phase 1: Infrastructure & ETL Pipeline — ✅ Completed

| Status | Task                                                                 |
|--------|----------------------------------------------------------------------|
| ✅     | Established a clean project structure with automated code formatting and linting. |
| ✅     | Designed and implemented modular data processing stages.|
| ✅     | Implemented centralized logging and error handling. |
| ✅     | Externalized configuration via `settings.yaml`, with optional overrides from `.env` files.|
| ✅     | Fully containerized all components using Docker and Docker Compose.  |
| ✅     | Integrated Jenkins for automated ETL runs, testing, and logging.   |
| ✅     | Added a Makefile with multi-purpose project commands." |
| 🟡     | Writing tests for all project modules. [▶ View Latest Test Results & Coverage](images/tests_passed.png)     |


### Phase 2: Intelligence & Model Evaluation — 🟡 In Progress

| Status | Task                                                                 |
|--------|----------------------------------------------------------------------|
| 🟡     | Generating custom input datasets for each model architecture. |
| 🔜     | Developing forecasting models using SARIMAX and Darts LSTM. |
| 🔜     | Comparing model predictions to actual outcomes using MAE and RMSE. |

### Phase 3: Expansion & Insight Delivery — 🔜 Upcoming

| Status | Task                                                                 |
|--------|----------------------------------------------------------------------|
| 🔜     | Exporting outputs to PostgreSQL for downstream analytics. |
| 🔜     | Building interactive dashboards with Power BI or Tableau. |

## 📦 How to `Run`

To list available commands:

```bash
make help
```


## 🔧 Tech Stack

| Category             | Tools & Libraries                   |
|----------------------|-------------------------------------|
| Language             | Python                              |
| Dependency Mgmt      | Poetry (`pyproject.toml`)           |
| Containers           | Docker, Docker Compose              |
| CI/CD                | Jenkins, GitHub                     |
| Testing Types        | Unit Testing, Integration Testing   |
| Testing Tools        | Pytest, pytest-cov, unittest.mock   |
| Code Quality         | Ruff, Black                         |
| Dev Workflow         | Makefile, Pre-commit                |
| Config Management    | `settings.yaml`, `.env`             |
| API Sources          | IP Geolocation API, Open-Meteo      |


### The Jenkinsfile:

-  [▶ View Jenkins Pipeline Console](images/jenkins_console.png)

- Cleans old data and logs
- Checks for .env file presence and falls back to defaults if missing
- Checks file structure before & after run

- Builds fresh Docker images for the app
- Builds fresh Docker images for tests
- Runs unit tests
- Runs integration tests

- Executes full ETL pipeline

- Archives cleaned data and logs (e.g. data/staging/*.csv, logs/*.log)
- Prints build metadata (time, ID, job info)

---
> Created and maintained by Mert, reflecting my approach to modular design, code quality, and CI/CD best practices.
