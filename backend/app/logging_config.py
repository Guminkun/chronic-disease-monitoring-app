import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "app.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
) -> logging.Logger:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if enable_file:
        log_path = LOG_DIR / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    access_log_path = LOG_DIR / "access.log"
    access_handler = logging.handlers.RotatingFileHandler(
        access_log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.addHandler(access_handler)

    error_log_path = LOG_DIR / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
