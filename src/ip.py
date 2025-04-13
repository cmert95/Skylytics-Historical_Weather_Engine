import requests
import json
import logging

logging.basicConfig(
    filename="logs/ip_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Retrieves city and postal information based on the public IP address.
def get_ip_info():
    url = "https://ipinfo.io/json"
    try:
        logging.info("Sending request to IPinfo API.")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        city = data.get("city")
        postal = data.get("postal")

        if city and postal:
            logging.info(f"Recuest success. City:{city}, Postal code:{postal}.")
            return {"city": city, "postal": postal}
        else:
            logging.error("City or postal information could not be retrieved.")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching IP info: {e}")
        return None


# Saves the city name to a text file
def save_location(location, filename="config/location.json"):
    if location:
        try:
            with open(filename, "w") as f:
                json.dump(location, f)
            logging.info(f"File saved successfully: {filename}.")
        except Exception as e:
            logging.error(f"Failed to save file to {filename}: {e}")
    else:
        logging.warning("No location information provided, nothing saved.")


if __name__ == "__main__":
    location = get_ip_info()
    save_location(location)
