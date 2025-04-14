# ⛈️ Weather Forecast Data Pipeline

This is a CI-enabled ETL pipeline that automatically collects and processes weather forecast data based on the user's IP location. It uses Docker and Jenkins to run containerized steps on a daily schedule, with customizable time intervals. The system is fully modular and designed for automation, observability, and future scalability.

## Project Overview

The project follows a 3-step structure:

1. **Location Detection (`ip.py`)**  

2. **Weather Data Retrieval (`weather.py`)**  

3. **Data Cleaning (`cleaning.py`)**  
   Cleans and interpolates the data to desired time intervals (e.g., 15min, 30min), adds location metadata, and outputs `.csv` and `.parquet` files.

## Technologies Used

- **Python**: `requests`, `pandas`, `dotenv`, `logging`
- **Docker**: Containerization of each ETL step
- **Docker Compose**: For running all steps as separate services
- **Jenkins**: For automating the pipeline via a `Jenkinsfile`
- **GitHub**: Code and CI/CD integration
- **APIs**: Source of raw data

###  Planned or In Progress

- **Power-BI** or **Tableau** 

## Running Locally

```bash
# Run each ETL step
docker compose run ip
docker compose run weather
docker compose run -e INTERVAL=15min cleaning
```

> 📝 Make sure `.env` file exists with your `API_KEY`.

## Jenkins Integration

This project includes a `Jenkinsfile` that:

- Runs each ETL step as a Docker Compose service
- Supports dynamic `INTERVAL` parameter
- Displays build info & workspace logs
- Runs daily at 08:30 AM on weekdays

---
I built this project to show how I like to build things.