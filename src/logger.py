import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(name=__name__, log_name="app", level=logging.INFO):
    """
    Sets up and returns a logger instance with file and console handlers.
    If log_name is provided, log will be written to logs/{log_name}.log
    """
    formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(name)s — %(message)s")

    log_file = LOG_DIR / f"{log_name}.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding handlers multiple times
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
