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
    except requests.exceptions.RequestException as e:
        logger.error(f"[FETCH] Failed to fetch IP info → {e}")
        return None

    city = data.get("city")
    postal = data.get("postal")
    loc = data.get("loc")

    if city and postal and loc:
        try:
            lat_str, lon_str = loc.split(",")
            latitude = float(lat_str.strip())
            longitude = float(lon_str.strip())
        except Exception as e:
            logger.error(f"[FETCH] Failed to parse coordinates → {e}")
            return None

        logger.info(f"[FETCH] Location fetched from IP → {city}, {postal}, {latitude}, {longitude}")
        return {"city": city, "postal": postal, "latitude": latitude, "longitude": longitude}
    else:
        logger.warning("[FETCH] Incomplete location info from IP API")
        return None


def save_location(location, path=SYSTEM_LOCATION_PATH):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(location, f, indent=2)
        logger.info(f"[SAVE] Location saved to → {path}")
    except Exception as e:
        logger.error(f"[SAVE] Failed to save location to {path} → {e}")


def read_location_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[CONFIG] Failed to read location file → {e}")
        return None


def load_location():
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


if __name__ == "__main__":
    location = load_location()
    if location:
        logger.info(f"[DONE] Final location resolved → {location}")
    else:
        logger.error("[ERROR] Could not resolve any location.")
