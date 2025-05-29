import json
from datetime import date, datetime, timedelta
from typing import Any, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import DAYS_TO_PULL, RAW_DATA_DIR, SYSTEM_LOCATION_PATH, TIMEZONE
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="weather_openmeteo_logs")

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_with_retry(
    url: str,
    params: dict[str, Any],
    retries: int = 3,
    backoff_factor: float = 0.5,
    timeout: int = 10,
) -> requests.Response:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response


def get_location_info(
    filename: str = SYSTEM_LOCATION_PATH,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            location: dict[str, Any] = json.load(f)

        lat: Optional[float] = location.get("latitude")
        lon: Optional[float] = location.get("longitude")
        postnum: Optional[str] = location.get("postal")

        if lat is None or lon is None or postnum is None:
            raise ValueError("Missing values in location file.")
        logger.info(f"[CONFIG] Location info loaded → lat: {lat}, lon: {lon}, postal: {postnum}")
        return lat, lon, postnum
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"[CONFIG] File system error → {e}")
    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] Malformed JSON → {e}")
    except (ValueError, TypeError) as e:
        logger.error(f"[CONFIG] Logical validation failed → {e}")
    except Exception as e:
        logger.error(f"[SAVE] Unknown error → {e.__class__.__name__}: {e}")
    return None, None, None


def get_weather_data(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
) -> Optional[dict[str, Any]]:
    """
    Fetches historical weather data from Open-Meteo API.
    """
    url: str = "https://archive-api.open-meteo.com/v1/archive"
    ALL_DAILY_VARIABLES: list[str] = [
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

    params: dict[str, Any] = {
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
        response: requests.Response = get_with_retry(url, params)
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


def save_to_file(data: dict[str, Any], filename: str) -> bool:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"[SAVE] Weather data saved to: {filename}")
        return True
    except (PermissionError, FileNotFoundError, OSError) as e:
        logger.error(f"[SAVE] File system error while saving → {e}")
        return False
    except (ValueError, TypeError) as e:
        logger.error(f"[SAVE] Serialization error (non-JSON serializable data?) → {e}")
        return False
    except Exception as e:
        logger.error(f"[SAVE] Unknown error → {e.__class__.__name__}: {e}")
        return False


def prepare_date_range() -> Tuple[str, str]:
    """
    Returns (start_date, end_date) string pairs based on DAYS_TO_PULL
    """
    end_date: date = date.today()
    start_date: date = end_date - timedelta(days=DAYS_TO_PULL)
    return start_date.isoformat(), end_date.isoformat()


def fetch_and_store_weather(lat: float, lon: float, postal: str) -> None:
    start_date, end_date = prepare_date_range()
    data = get_weather_data(lat, lon, start_date, end_date)

    if not data:
        logger.error("[PIPELINE] No data fetched. Aborting save.")
        return

    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d_%H-%M")
    filename = RAW_DATA_DIR / f"raw_weather_{postal}_{timestamp}.json"
    save_to_file(data, str(filename))


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
