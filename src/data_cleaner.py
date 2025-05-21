import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

import pandas as pd

from src.config import RAW_DATA_DIR, STAGING_DATA_DIR, SYSTEM_LOCATION_PATH, TIMEZONE
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="data_cleaner")


def get_latest_raw_file(directory: Path) -> Optional[Path]:
    files = list(directory.glob("raw_weather_*.json"))
    if not files:
        logger.error("[FILE] No raw weather files found.")
        return None
    latest = max(files, key=lambda f: f.stat().st_ctime)
    logger.info(f"[FILE] Latest raw file selected: {latest}")
    return latest


def load_location_info(filepath: Path) -> Tuple[Optional[str], Optional[str]]:
    if not filepath.exists():
        logger.error(f"[CONFIG] File not found: {filepath}")
        return None, None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"[CONFIG] File access error → {e}")
        return None, None
    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] Invalid JSON: {e}")
        return None, None
    except Exception as e:
        logger.error(f"[CONFIG] Unexpected error → {e.__class__.__name__}: {e}")
        return None, None

    city = data.get("city")
    postal = data.get("postal")
    if not city or not postal:
        logger.error("[CONFIG] Missing 'city' or 'postal' field.")
        return None, None

    logger.info(f"[CONFIG] Loaded city & postal → {city}, {postal}")
    return city, postal


def load_raw_weather(filepath: Path) -> Optional[dict[str, Any]]:
    if not filepath.exists():
        logger.error(f"[LOAD] File does not exist: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
        logger.info(f"[LOAD] Raw weather data loaded from {filepath}")
        return data
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"[LOAD] File access error → {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"[LOAD] Invalid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"[LOAD] Unexpected error → {e.__class__.__name__}: {e}")
        return None


def build_dataframe(raw_data: dict[str, Any], city: str, postal: str) -> pd.DataFrame:
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

    if not daily:
        logger.error("[BUILD] Missing 'daily' section in raw weather data.")
        return pd.DataFrame()

    missing_keys = [k for k in required_keys if k not in daily]
    if missing_keys:
        logger.error(f"[BUILD] Missing keys in 'daily': {missing_keys}")
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

    logger.info(f"[BUILD] DataFrame constructed with {len(df)} rows.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Convert Date to datetime
    df["Date"] = pd.to_datetime(df["Date"])
    logger.debug("[CLEAN] Converted 'Date' to datetime")

    # Filter out extreme values
    original_len = len(df)
    df = df[(df["Temp_Max_C"] <= 60) & (df["Temp_Min_C"] >= -30) & (df["WindSpeed_Max_kph"] < 200)]
    logger.info(f"[CLEAN] Removed {original_len - len(df)} rows with extreme values")

    # Interpolate numeric columns
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear").round(1)
    logger.debug(f"[CLEAN] Interpolated numeric columns: {list(numeric_cols)}")

    # Fill non-numeric nulls
    non_numeric_cols = df.select_dtypes(exclude="number").columns
    df[non_numeric_cols] = df[non_numeric_cols].ffill()
    logger.debug(f"[CLEAN] Forward-filled non-numeric columns: {list(non_numeric_cols)}")

    # Sort and reset index
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"[CLEAN] DataFrame ready. Final row count: {len(df)}")

    return df


def save_cleaned_data(df: pd.DataFrame) -> bool:
    STAGING_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")

    csv_path = STAGING_DATA_DIR / f"cleaned_weather_{timestamp}.csv"

    try:
        df.to_csv(csv_path, index=False)
        logger.info(f"[SAVE] File written to: {csv_path}")
        return True
    except (PermissionError, FileNotFoundError, OSError) as e:
        logger.error(f"[SAVE] File access error → {e}")
        return False
    except (ValueError, TypeError) as e:
        logger.error(f"[SAVE] Data format issue → {e}")
        return False
    except Exception as e:
        logger.error(f"[SAVE] Unexpected error → {e.__class__.__name__}: {e}")
        return False


def run() -> bool:
    raw_file = get_latest_raw_file(RAW_DATA_DIR)
    if not raw_file:
        logger.error("[ERROR] No raw file found.")
        return False

    city, postal = load_location_info(SYSTEM_LOCATION_PATH)
    if not city or not postal:
        logger.error("[ERROR] Invalid location metadata.")
        return False

    raw_data = load_raw_weather(raw_file)
    if not raw_data:
        logger.error("[ERROR] Failed to load raw weather data.")
        return False

    df = build_dataframe(raw_data, city, postal)
    if df.empty:
        logger.error("[ERROR] Empty DataFrame after building.")
        return False

    df = clean_data(df)
    if df.empty:
        logger.error("[ERROR] Empty DataFrame after cleaning.")
        return False

    save_cleaned_data(df)
    logger.info("[DONE] Cleaned data saved successfully.")
    return True


if __name__ == "__main__":
    run()
