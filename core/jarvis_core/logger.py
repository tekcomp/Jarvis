# jarvis_core/logger.py
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "jarvis.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_info(message: str):
    logging.info(message)

def log_error(message: str):
    logging.error(message)
