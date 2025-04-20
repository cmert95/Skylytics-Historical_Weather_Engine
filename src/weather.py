import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

TIMEZONE = ZoneInfo("Europe/Berlin")

logging.basicConfig(
    filename="logs/weather_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Retrieves the API key from environment variables
def get_api_key():
    api_key = os.getenv("API_KEY")
    if api_key:
        logging.info("API key successfully retrieved.")
        return api_key
    else:
        logging.error("API key could not be retrieved.")
        return None


# Reads the city name and postal code from a json file
def get_infos_from_json(filename="config/location.json"):
    try:
        with open(filename, "r") as f:
            location = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error reading location file: {e}")
        return None, None

    city = location.get("city")
    postal = location.get("postal")

    if not city or not postal:
        logging.error("City or postal information is missing in JSON.")
        return None, None

    logging.info(f"Location retrieved: {city}, Postal: {postal}.")
    return city, postal


# fmt: off
# Makes a request to the weather API to retrieve forecast
# Free plan supports a maximum of 3 days forecast.
# Forecast always starts from today.
def get_forecast(city, api_key):
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": city,
        "days": 1,
        "aqi": "no",
        "alerts": "no"
    }
# fmt: on

    try:
        logging.info(f"Requesting weather data for city: {city}")
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API request failed: {e}")
        return None


# Main function to coordinate the workflow and save the file.
def save_forecast_to_json():
    city, postal = get_infos_from_json()
    api_key = get_api_key()

    if not city or not postal:
        logging.error("City or postal code is missing. Exiting process.")
        return

    if not api_key:
        logging.error("API key is missing. Exiting process.")
        return

    forecast_data = get_forecast(city, api_key)

    if forecast_data:
        local_now = datetime.now(TIMEZONE)
        file_name = f"data/raw/raw_weather_{local_now.strftime('%d%m%Y')}.json"
        try:
            with open(file_name, "w") as f:
                json.dump(forecast_data, f)
            logging.info(f"Forecast data saved successfully (JSON): {file_name}")
        except Exception as e:
            logging.error(f"Failed to save forecast data to {file_name}: {e}")
    else:
        logging.error("Forecast data could not be retrieved.")


if __name__ == "__main__":
    save_forecast_to_json()
