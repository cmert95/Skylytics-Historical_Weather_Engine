import os
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SYSTEM_LOCATION_PATH = Path(os.getenv("SYSTEM_LOCATION_PATH", "data/sources/location.json"))
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR", "data/sources"))
STAGING_DATA_DIR = Path(os.getenv("STAGING_DATA_DIR", "data/staging"))
WAREHOUSE_DATA_DIR = Path(os.getenv("WAREHOUSE_DATA_DIR", "data/warehouse"))
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))


def load_yaml_config(path=BASE_DIR / "config" / "settings.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


SETTINGS = load_yaml_config()
DAYS_TO_PULL = int(os.getenv("DAYS_TO_PULL", SETTINGS.get("weather", {}).get("days_to_pull", 90)))

TIMEZONE_NAME = os.getenv("TIMEZONE", SETTINGS.get("timezone", "Europe/Berlin"))
TIMEZONE = ZoneInfo(TIMEZONE_NAME)
