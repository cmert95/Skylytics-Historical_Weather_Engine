import json
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from src.config import DAYS_TO_PULL, RAW_DATA_DIR, SYSTEM_LOCATION_PATH
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="weather_openmeteo_logs")

TIMEZONE = ZoneInfo("Europe/Berlin")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_location_info(filename=SYSTEM_LOCATION_PATH):
    try:
        with open(filename, "r") as f:
            location = json.load(f)
        lat = location.get("latitude")
        lon = location.get("longitude")
        postnum = location.get("postal")
        if lat is None or lon is None or postnum is None:
            raise ValueError("Missing values in config file.")
        logger.info(f"Informations retrieved: {lat}, {lon}, {postnum}")
        return lat, lon, postnum
    except Exception as e:
        logger.error(f"Error loading location information: {e}")
        return None, None, None


def prepare_date_range():
    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_TO_PULL)
    return start_date.isoformat(), end_date.isoformat()


def get_weather_data(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    ALL_DAILY_VARIABLES = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "windspeed_10m_max",
        "shortwave_radiation_sum",
        "sunshine_duration",
    ]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(ALL_DAILY_VARIABLES),
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


def save_to_file(data, filename):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Weather data saved to: {filename}")
    except Exception as e:
        logger.error(f"Failed to save weather data: {e}")


def fetch_and_store_weather(lat, lon, postal):
    start_date, end_date = prepare_date_range()
    data = get_weather_data(lat, lon, start_date, end_date)

    if not data:
        logger.error("No data fetched. Exiting.")
        return

    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d_%H-%M")
    filename = RAW_DATA_DIR / f"raw_weather_{postal}_{timestamp}.json"
    save_to_file(data, filename)


def run():
    lat, lon, postal = get_location_info()
    if not lat or not lon:
        logger.error("Coordinates not found. Exiting.")
        return

    if not postal:
        logger.error("Postal not found. Exiting.")
        return

    fetch_and_store_weather(lat, lon, postal)


if __name__ == "__main__":
    run()
