import json

import requests

from src.logger import setup_logger

logger = setup_logger(__name__, log_name="ip_logs")


# Retrieves city and postal information based on the public IP address.
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

    if city and postal:
        logger.info(f"Request successful. City: {city}, Postal code: {postal}.")
        return {"city": city, "postal": postal}
    else:
        logger.warning("City or postal information could not be retrieved.")
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
