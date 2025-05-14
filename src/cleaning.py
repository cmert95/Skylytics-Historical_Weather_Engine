import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from src.logger import setup_logger

RAW_DATA_DIR = Path("data/raw")
CONFIG_PATH = Path("config/location.json")
CLEANED_DATA_DIR = Path("data/cleaned")
TIMEZONE = ZoneInfo("Europe/Berlin")

logger = setup_logger(__name__, log_name="cleaning_logs")


# Find the most recent raw json file
def get_latest_raw_file(directory):
    files = list(directory.glob("raw_weather_*.json"))
    if not files:
        logger.error("No raw weather files found.")
        return None
    latest = max(files, key=lambda f: f.stat().st_ctime)
    logger.info(f"Latest raw file: {latest}")
    return latest


def load_location_info(filepath):
    if not filepath.exists():
        logger.error(f"Config file not found: {filepath}")
        return None, None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return None, None

    city = data.get("city")
    postal = data.get("postal")
    if not city or not postal:
        logger.error("Missing 'city' or 'postal' in location config.")
        return None, None

    logger.info(f"Location info retrieved: {city}, {postal}")
    return city, postal


def load_raw_weather(filepath):
    if not filepath.exists():
        logger.error(f"Raw data file does not exist: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded raw data from: {filepath}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse raw JSON: {e}")
        return None


def build_dataframe(raw_data, city, postal):
    daily = raw_data.get("daily")

    required_keys = [
        "time",
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

    daily = raw_data.get("daily")
    if not daily:
        logger.error("Missing 'daily' section in raw weather data.")
        return pd.DataFrame()

    missing_keys = [k for k in required_keys if k not in daily]
    if missing_keys:
        logger.error(f"Missing required keys in 'daily': {missing_keys}")
        return pd.DataFrame()

    df = pd.DataFrame(
        {
            "Date": daily["time"],
            "Temp_Max_C": daily["temperature_2m_max"],
            "Temp_Min_C": daily["temperature_2m_min"],
            "Temp_Mean_C": daily["temperature_2m_mean"],
            "Precipitation_mm": daily["precipitation_sum"],
            "Rain_mm": daily["rain_sum"],
            "Snowfall_mm": daily["snowfall_sum"],
            "WindSpeed_Max_kph": daily["windspeed_10m_max"],
            "Radiation_Sum_kWh": daily["shortwave_radiation_sum"],
            "Sunshine_Minutes": daily["sunshine_duration"],
        }
    )

    df["City"] = city
    df["PostalCode"] = postal

    logger.info("DataFrame constructed successfully with %d rows.", len(df))
    return df


def clean_data(df):
    # Convert Date to datetime
    df["Date"] = pd.to_datetime(df["Date"])
    logger.debug("Converted 'Date' column to datetime.")

    # Filter out extreme values
    original_len = len(df)
    df = df[(df["Temp_Max_C"] <= 60) & (df["Temp_Min_C"] >= -30) & (df["WindSpeed_Max_kph"] < 200)]
    filtered_len = len(df)
    logger.info("Filtered out %d rows with extreme values.", original_len - filtered_len)

    # Interpolate numeric columns
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear").round(1)
    logger.debug("Interpolated numeric columns: %s", list(numeric_cols))

    # Fill non-numeric nulls
    non_numeric_cols = df.select_dtypes(exclude="number").columns
    df[non_numeric_cols] = df[non_numeric_cols].ffill()
    logger.debug("Forward-filled non-numeric columns: %s", list(non_numeric_cols))

    # Sort and reset index
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info("Data cleaning completed. Final row count: %d", len(df))

    return df


def save_cleaned_data(df):
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")

    csv_path = CLEANED_DATA_DIR / f"cleaned_weather_{timestamp}.csv"

    try:
        df.to_csv(csv_path, index=False)
        logger.info(f"Cleaned data saved to CSV: {csv_path}")
    except Exception as e:
        logger.error(f"Failed to save cleaned data to CSV: {e}")


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

    df = build_dataframe(raw_data, city, postal)
    if df.empty:
        logger.error("DataFrame is empty after building.")
        return

    df = clean_data(df)
    if df.empty:
        logger.error("No data to save. DataFrame is empty after cleaning.")
        return

    save_cleaned_data(df)


if __name__ == "__main__":
    main()
