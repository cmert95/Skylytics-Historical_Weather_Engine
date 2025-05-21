import json
from pathlib import Path

import requests

from src.config import SETTINGS, SYSTEM_LOCATION_PATH
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="ip_logs")


def fetch_location_from_ip():
    url = "https://ipinfo.io/json"
    logger.info("[FETCH] Fetching location from IPinfo API")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
    ) as e:
        logger.error(f"[FETCH] API request failed → {e}")
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

        logger.info(f"[FETCH] Location fetched from IP → {city}, {postal}, {latitude}, {longitude}")
        return {"city": city, "postal": postal, "latitude": latitude, "longitude": longitude}
    else:
        logger.warning("[FETCH] Incomplete location info from IP API")
        return None


def save_location(location, path=SYSTEM_LOCATION_PATH):
    if not location:
        logger.warning("[SAVE] No location information provided.")
        return False
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(location, f, indent=2)
        logger.info(f"[SAVE] Location saved to → {path}")
        return True
    except (OSError, PermissionError) as e:
        logger.error(f"[SAVE] File system error while saving → {e}")
        return False
    except TypeError as e:
        logger.error(f"[SAVE] Serialization error → {e}")
        return False


def read_location_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"[CONFIG] Failed to read location file → {path}")
        # TODO: Change this message to "Location file not found" after updating the test
        return None
    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] Invalid JSON format in location file → {e}")
        return None
    except OSError as e:
        logger.error(f"[CONFIG] Error reading file → {e}")
        return None


def resolve_location():
    # 1. Try from settings.yaml
    loc = SETTINGS.get("location", {})
    lat, lon, postal = loc.get("latitude"), loc.get("longitude"), loc.get("postal")

    if lat and lon and postal:
        logger.info("[CONFIG] Location loaded from settings.yaml")
        return {"latitude": lat, "longitude": lon, "postal": postal}

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


def run() -> dict | None:
    location = resolve_location()
    if not location:
        logger.error("[ERROR] Could not resolve any location.")
        return None
    logger.info(f"[DONE] Final location resolved → {location}")
    return location


if __name__ == "__main__":
    run()
