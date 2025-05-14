import json
import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

RAW_DATA_DIR = Path("data/raw")
CONFIG_PATH = Path("config/location.json")
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
    try:
        # Flatten hourly forecast
        records = []
        for day in raw_data["forecast"]["forecastday"]:
            for hour in day["hour"]:
                records.append(hour)

        df = pd.json_normalize(records)

        # Rename columns
        df = df[["time", "temp_c", "condition.text", "humidity", "wind_kph", "feelslike_c"]]
        df.columns = [
            "DateTime",
            "Temperature_C",
            "Condition",
            "Humidity_perc",
            "WindSpeed_kph",
            "FeelsLike_C",
        ]

        # Parse datetime
        df["DateTime"] = pd.to_datetime(df["DateTime"])

        # Clean condition labels
        df["Condition"] = df["Condition"].str.strip().str.title()

        # Add city and postal code
        df["City"] = city
        df["PostalCode"] = postal

        # Drop unrealistic temperature values
        df = df[(df["Temperature_C"] <= 60) & (df["Temperature_C"] >= -30)]

        # Resample
        df.set_index("DateTime", inplace=True)
        interval = os.getenv("INTERVAL", "30min")
        df = df.resample(interval).asfreq()

        # Filling numeric columns
        num_cols = df.select_dtypes(include="number").columns
        df[num_cols] = df[num_cols].interpolate(method="linear").round(1)

        # Filling non-numeric columns
        non_num_cols = df.select_dtypes(exclude="number").columns
        df[non_num_cols] = df[non_num_cols].ffill()

        df.reset_index(inplace=True)
        logging.info("Forecast data cleaned and interpolated successfully.")
        return df

    except Exception as e:
        logging.error(f"Data cleaning failed: {e}")
        return pd.DataFrame()


# Save cleaned data to CSV and Parquet
def save_cleaned_data(df):
    local_now = datetime.now(ZoneInfo("Europe/Berlin"))
    timestamp = local_now.strftime("%d%m%Y_%H%M%S")
    csv_path = f"data/cleaned/cleaned_weather_{timestamp}.csv"
    parquet_path = f"data/cleaned/cleaned_weather_{timestamp}.parquet"

    try:
        df.to_csv(csv_path, index=False)
        logging.info(f"Cleaned data saved to CSV: {csv_path}")
    except Exception as e:
        logging.error(f"Failed to save cleaned data to CSV: {e}")

    try:
        df.to_parquet(parquet_path, index=False)
        logging.info(f"Cleaned data saved to Parquet: {parquet_path}")
    except Exception as e:
        logging.error(f"Failed to save cleaned data to Parquet: {e}")


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


if __name__ == "__main__":
    main()
