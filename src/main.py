from src.data_cleaner import run as clean_weather_data
from src.location_resolver import run as resolve_location
from src.logger import setup_logger
from src.weather_data_fetcher import run as fetch_weather_data

logger = setup_logger(__name__, log_name="pipeline")


def main():
    logger.info("[PIPELINE] Starting data pipeline")

    try:
        logger.info("[STEP 1] Resolving location")
        location = resolve_location()
        if not location:
            logger.error("[ABORT] Location step failed.")
            return

        logger.info("[STEP 2] Fetching weather data")
        if not fetch_weather_data():
            logger.error("[ABORT] Weather data fetch step failed.")
            return

        logger.info("[STEP 3] Cleaning and saving data")
        if not clean_weather_data():
            logger.error("[ABORT] Data cleaning step failed.")
            return

        logger.info("[PIPELINE DONE] All steps completed successfully")

    except Exception as e:
        logger.exception(f"[PIPELINE ERROR] Unhandled exception → {e}")
        raise


if __name__ == "__main__":
    main()
