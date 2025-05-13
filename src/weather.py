import json
from pathlib import Path

import requests

from src.logger import setup_logger

logger = setup_logger(__name__, log_name="weather_openmeteo_logs")

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Load lat/lon from config
def get_coordinates(filename=Path("config/location.json")):
    try:
        with open(filename, "r") as f:
            location = json.load(f)
        lat = location.get("latitude")
        lon = location.get("longitude")
        if lat is None or lon is None:
            raise ValueError("Missing latitude or longitude in config file.")
        logger.info(f"Coordinates retrieved: {lat}, {lon}")
        return lat, lon
    except Exception as e:
        logger.error(f"Error loading coordinates: {e}")
        return None, None


# Fetch historical data from Open-Meteo
def get_weather_data(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Berlin",
    }

    logger.info(f"Requesting weather data from {start_date} to {end_date} for lat:{lat}, lon:{lon}")
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        logger.info("Data fetched successfully from Open-Meteo.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data: {e}")
        return None


# Save to data/raw
def save_to_file(data, filename):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Weather data saved to: {filename}")
    except Exception as e:
        logger.error(f"Failed to save weather data: {e}")


def run():
    lat, lon = get_coordinates()
    if not lat or not lon:
        logger.error("Coordinates not found. Exiting.")
        return

    start_date = "2023-04-01"
    end_date = "2024-04-10"

    data = get_weather_data(lat, lon, start_date, end_date)
    if not data:
        logger.error("No data fetched. Exiting.")
        return

    filename = RAW_DATA_DIR / f"openmeteo_weather_{start_date}_to_{end_date}.json"
    save_to_file(data, filename)


if __name__ == "__main__":
    run()
