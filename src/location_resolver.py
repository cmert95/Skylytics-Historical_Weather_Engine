import json
from pathlib import Path
from typing import Any, Optional, TypedDict, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import SETTINGS, SYSTEM_LOCATION_PATH
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="ip_logs")


class LocationDict(TypedDict):
    city: str
    postal: str
    latitude: float
    longitude: float


def get_with_retry(
    url: str, retries: int = 3, backoff_factor: float = 0.5, timeout: int = 10
) -> requests.Response | None:
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

    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"[FETCH] Request to {url} failed: {e}")
        return None


def fetch_location_from_ip() -> Optional[LocationDict]:
    url: str = "https://ipinfo.io/json"
    logger.info("[FETCH] Fetching location from IPinfo API")
    try:
        response: Optional[requests.Response] = get_with_retry(url)
        if response is None:
            return None
        data: dict[str, Any] = response.json()
    except (
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
    ) as e:
        logger.error(f"[FETCH] API request failed → {e}")
        return None
    except Exception as e:
        logger.error(f"[FETCH] Unexpected error → {e.__class__.__name__}: {e}")
        return None

    city = data.get("city")
    postal = data.get("postal")
    loc = data.get("loc")

    if city and postal and loc:
        try:
            lat_str, lon_str = loc.split(",")
            latitude = float(lat_str.strip())
            longitude = float(lon_str.strip())
        except (ValueError, AttributeError) as e:
            logger.error(f"[FETCH] Failed to parse coordinates → {e}")
            return None
        except Exception as e:
            logger.error(f"[FETCH] Unexpected error → {e.__class__.__name__}: {e}")
            return None

        logger.info(f"[FETCH] Location fetched from IP → {city}, {postal}, {latitude}, {longitude}")
        return {"city": city, "postal": postal, "latitude": latitude, "longitude": longitude}
    else:
        logger.warning("[FETCH] Incomplete location info from IP API")
        return None


def save_location(
    location: Optional[LocationDict], path: Union[str, Path] = SYSTEM_LOCATION_PATH
) -> bool:
    if not location:
        logger.warning("[SAVE] No location information provided.")
        return False
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(location, f, indent=2)
        logger.info(f"[SAVE] Location saved to → {path}")
        return True
    except (PermissionError, FileNotFoundError, OSError) as e:
        logger.error(f"[SAVE] File system error while saving → {e}")
        return False
    except (ValueError, TypeError) as e:
        logger.error(f"[SAVE] Data format issue → {e}")
        return False
    except Exception as e:
        logger.error(f"[SAVE] Unexpected error → {e.__class__.__name__}: {e}")
        return False


def read_location_file(path: Union[str, Path]) -> Optional[LocationDict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (PermissionError, FileNotFoundError) as e:
        logger.warning(f"[CONFIG] Location file not found → {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] Invalid JSON format in location file → {e}")
        return None
    except OSError as e:
        logger.error(f"[CONFIG] Error reading file → {e}")
        return None
    except Exception as e:
        logger.error(f"[CONFIG] Unexpected error → {e.__class__.__name__}: {e}")
        return None


def resolve_location() -> Optional[LocationDict]:
    # 1. Try from settings.yaml
    loc = SETTINGS.get("location", {})
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    postal = loc.get("postal")
    city = loc.get("city", "Unknown")

    if lat and lon and postal and city:
        logger.info("[CONFIG] Location loaded from settings.yaml")
        return {"latitude": lat, "longitude": lon, "postal": postal, "city": city}

    # 2. Try from cached file
    if Path(SYSTEM_LOCATION_PATH).exists():
        logger.info("[CONFIG] Using cached location from disk")
        return read_location_file(SYSTEM_LOCATION_PATH)

    # 3. Fallback to IP lookup
    logger.info("[CONFIG] No config or cache found. Falling back to IP-based location")
    location = fetch_location_from_ip()
    if location:
        save_location(location)
    return location


def run() -> Optional[LocationDict]:
    location = resolve_location()
    if not location:
        logger.error("[ERROR] Could not resolve any location.")
        return None
    logger.info(f"[DONE] Final location resolved → {location}")
    return location


if __name__ == "__main__":
    run()
