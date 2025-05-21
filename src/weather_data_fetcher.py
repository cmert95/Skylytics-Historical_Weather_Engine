import json
from datetime import date, datetime, timedelta

import requests

from src.config import DAYS_TO_PULL, RAW_DATA_DIR, SYSTEM_LOCATION_PATH, TIMEZONE
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="weather_openmeteo_logs")

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_location_info(filename=SYSTEM_LOCATION_PATH):
    try:
        with open(filename, "r") as f:
            location = json.load(f)
        lat = location.get("latitude")
        lon = location.get("longitude")
        postnum = location.get("postal")
        if lat is None or lon is None or postnum is None:
            raise ValueError("Missing values in location file.")
        logger.info(f"[CONFIG] Location info loaded → lat: {lat}, lon: {lon}, postal: {postnum}")
        return lat, lon, postnum
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"[CONFIG] File access issue → {e}")
        return None, None, None
    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] Malformed JSON → {e}")
        return None, None, None
    except ValueError as e:
        logger.error(f"[CONFIG] Logical validation failed → {e}")
        return None, None, None
    except OSError as e:
        logger.error(f"[CONFIG] OS-level file error → {e}")
        return None, None, None


def get_weather_data(lat, lon, start_date, end_date):
    """
    Fetches historical weather data from Open-Meteo API.
    """
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

    logger.info(
        f"[FETCH] Requesting weather data: {start_date} → {end_date} | lat:{lat}, lon:{lon}"
    )
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        logger.info("[FETCH] Data fetched successfully from Open-Meteo API")
        return response.json()
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        logger.error(f"[FETCH] Network error during request → {e}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"[FETCH] HTTP error → {e.response.status_code}: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"[FETCH] Unexpected request exception → {e}")
        return None


def save_to_file(data, filename) -> bool:
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"[SAVE] Weather data saved to: {filename}")
        return True
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"[SAVE] File access issue → {e}")
    except TypeError as e:
        logger.error(f"[SAVE] Serialization error (non-JSON serializable data?) → {e}")
    except OSError as e:
        logger.error(f"[SAVE] File write error → {e}")
    return False


def prepare_date_range():
    """
    Returns (start_date, end_date) string pairs based on DAYS_TO_PULL
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_TO_PULL)
    return start_date.isoformat(), end_date.isoformat()


def fetch_and_store_weather(lat, lon, postal):
    start_date, end_date = prepare_date_range()
    data = get_weather_data(lat, lon, start_date, end_date)

    if not data:
        logger.error("[PIPELINE] No data fetched. Aborting save.")
        return

    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d_%H-%M")
    filename = RAW_DATA_DIR / f"raw_weather_{postal}_{timestamp}.json"
    save_to_file(data, filename)


def run() -> bool:
    lat, lon, postal = get_location_info()
    if not lat or not lon:
        logger.error("[ERROR] Coordinates missing. Exiting.")
        return False

    if not postal:
        logger.error("[ERROR] Postal code missing. Exiting.")
        return False

    fetch_and_store_weather(lat, lon, postal)
    logger.info("[DONE] Weather data fetched and saved successfully.")
    return True


if __name__ == "__main__":
    run()
