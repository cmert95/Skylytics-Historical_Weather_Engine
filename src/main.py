from src.data_cleaner import run as clean_weather_data
from src.location_resolver import run as resolve_location
from src.logger import setup_logger
from src.weather_data_fetcher import run as fetch_weather_data

logger = setup_logger(__name__, log_name="pipeline")


def main():
    logger.info("[PIPELINE] Starting data pipeline")

    resolve_location()
    logger.info("[STEP 1 DONE] Location resolved")

    fetch_weather_data()
    logger.info("[STEP 2 DONE] Weather data fetched")

    clean_weather_data()
    logger.info("[STEP 3 DONE] Data cleaned and saved")

    logger.info("[PIPELINE DONE] All steps completed successfully")


if __name__ == "__main__":
    main()
