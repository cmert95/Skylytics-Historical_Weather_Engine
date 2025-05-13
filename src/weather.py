import json
from pathlib import Path

import requests

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_coordinates(filename=Path("config/location.json")):
    with open(filename, "r") as f:
        location = json.load(f)
    lat = location.get("latitude")
    lon = location.get("longitude")
    if lat is None or lon is None:
        raise ValueError("Missing latitude or longitude in config file.")
    return lat, lon


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

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def save_to_file(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def run():
    lat, lon = get_coordinates()
    start_date = "2024-04-01"
    end_date = "2024-04-10"
    data = get_weather_data(lat, lon, start_date, end_date)
    filename = RAW_DATA_DIR / f"openmeteo_weather_{start_date}_to_{end_date}.json"
    save_to_file(data, filename)


if __name__ == "__main__":
    run()
