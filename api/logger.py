#!/usr/bin/python3

import logging
from logging.handlers import RotatingFileHandler
import os

LOGFILE = os.getenv("LOGFILE", "app.log")
MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))  # 5 MB default
BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

def get_logger(name=None):
    """Return a logger configured with rotation and console output.

    Args:
        name (str, optional): Logger name. Defaults to None.

    Returns:
        logging.Logger: Logger set to INFO with file and console handlers.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    fh = RotatingFileHandler(
        LOGFILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
