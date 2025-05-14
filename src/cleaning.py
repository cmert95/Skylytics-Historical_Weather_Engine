import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

RAW_DATA_DIR = Path("data/raw")
CONFIG_PATH = Path("config/location.json")
CLEANED_DATA_DIR = Path("data/cleaned")
TIMEZONE = ZoneInfo("Europe/Berlin")

logging.basicConfig(
    filename="logs/cleaning_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Find the most recent raw json file
def get_latest_raw_file(directory):
    files = list(directory.glob("raw_weather_*.json"))
    if not files:
        logging.error("No raw weather files found.")
        return None
    latest = max(files, key=lambda f: f.stat().st_ctime)
    logging.info(f"Latest raw file: {latest}")
    return latest


def load_location_info(filepath):
    if not filepath.exists():
        logging.error(f"Config file not found: {filepath}")
        return None, None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file: {e}")
        return None, None

    city = data.get("city")
    postal = data.get("postal")
    if not city or not postal:
        logging.error("Missing 'city' or 'postal' in location config.")
        return None, None

    logging.info(f"Location info retrieved: {city}, {postal}")
    return city, postal


def load_raw_weather(filepath):
    if not filepath.exists():
        logging.error(f"Raw data file does not exist: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Loaded raw data from: {filepath}")
        return data
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse raw JSON: {e}")
        return None


def clean_data(raw_data, city, postal):
    daily = raw_data.get("daily")
    required_keys = ["time", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"]

    if not daily or not all(k in daily for k in required_keys):
        logging.error("Missing expected keys in 'daily' section of raw data.")
        return pd.DataFrame()

    df = pd.DataFrame(
        {
            "Date": daily["time"],
            "Temp_Max_C": daily["temperature_2m_max"],
            "Temp_Min_C": daily["temperature_2m_min"],
            "Precipitation_mm": daily["precipitation_sum"],
        }
    )

    df["City"] = city
    df["PostalCode"] = postal

    logging.info("Weather data cleaned successfully.")
    return df


# Save cleaned data to CSV and Parquet
def save_cleaned_data(df):
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")

    csv_path = CLEANED_DATA_DIR / f"cleaned_weather_{timestamp}.csv"

    try:
        df.to_csv(csv_path, index=False)
        logging.info(f"Cleaned data saved to CSV: {csv_path}")
    except Exception as e:
        logging.error(f"Failed to save cleaned data to CSV: {e}")


def main():
    raw_file = get_latest_raw_file(RAW_DATA_DIR)
    if not raw_file:
        return

    city, postal = load_location_info(CONFIG_PATH)
    if not city or not postal:
        return

    raw_data = load_raw_weather(raw_file)
    if not raw_data:
        return

    df = clean_data(raw_data, city, postal)
    if df.empty:
        logging.error("No data to save. DataFrame is empty.")
        return

    save_cleaned_data(df)


if __name__ == "__main__":
    main()
