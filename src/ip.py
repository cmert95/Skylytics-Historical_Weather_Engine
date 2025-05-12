import json

import requests

from src.logger import setup_logger

logger = setup_logger(__name__, log_name="ip_logs")


# Retrieves city, postal and location information based on the public IP address.
def get_ip_info():
    url = "https://ipinfo.io/json"
    logger.info("Sending request to IPinfo API.")
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

        logger.info(
            f"Request successful. City: {city}, Postal code: {postal}, Lat: {latitude}, Lon: {longitude}."
        )
        return {"city": city, "postal": postal, "latitude": latitude, "longitude": longitude}
    else:
        logger.warning("Some location fields are missing in the response.")
        return None


# Saves the city and postal info to a JSON config file
def save_location(location, filename="config/location.json"):
    if not location:
        logger.warning("No location information provided, nothing saved.")
        return

    try:
        with open(filename, "w") as f:
            json.dump(location, f)
        logger.info(f"File saved successfully: {filename}")
    except Exception as e:
        logger.error(f"Failed to save file to {filename}: {e}")


if __name__ == "__main__":
    location = get_ip_info()
    save_location(location)
