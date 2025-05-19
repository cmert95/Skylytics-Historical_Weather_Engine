import json
from pathlib import Path

import requests

from src.config import SETTINGS, SYSTEM_LOCATION_PATH
from src.logger import setup_logger

logger = setup_logger(__name__, log_name="ip_logs")


def fetch_location_from_ip():
    url = "https://ipinfo.io/json"
    logger.info("Fetching location from IPinfo API")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching IP info: {e}")
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
            logger.error(f"Failed to parse coordinates: {e}")
            return None

        return {"city": city, "postal": postal, "latitude": latitude, "longitude": longitude}
    else:
        logger.warning("Incomplete location info from IP API")
        return None


def save_location(location, path=SYSTEM_LOCATION_PATH):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(location, f)
        logger.info(f"Location saved to {path}")
    except Exception as e:
        logger.error(f"Failed to save location to {path}: {e}")


def read_location_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read location file: {e}")
        return None


def load_location():
    loc = SETTINGS.get("location", {})
    lat, lon, postal = loc.get("latitude"), loc.get("longitude"), loc.get("postal")

    if lat and lon and postal:
        logger.info("Loaded location from settings.yaml")
        return {"latitude": lat, "longitude": lon, "postal": postal}

    if Path(SYSTEM_LOCATION_PATH).exists():
        logger.info("Using cached location file")
        return read_location_file(SYSTEM_LOCATION_PATH)

    logger.info("No location in settings or cache. Using IP lookup")
    location = fetch_location_from_ip()
    if location:
        save_location(location)
    return location


if __name__ == "__main__":
    location = load_location()
    if location:
        logger.info(f"Final resolved location: {location}")
    else:
        logger.error("Could not resolve any location")
