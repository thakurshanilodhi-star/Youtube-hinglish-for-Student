"""Utility functions."""
import logging
import sys
from app.config import get_settings

settings = get_settings()

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )
    return logging.getLogger("hinglish_dub")

logger = setup_logging()
