import logging
import sys

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup a logger with consistent formatting"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s [%(name)s] %(message)s",
            "%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
