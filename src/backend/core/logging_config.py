import logging
import logging.handlers
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def setup_logging():
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    app_file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "app.log", maxBytes=1024 * 1024 * 10, backupCount=5
    )
    app_file_handler.setFormatter(logging.Formatter(log_format))
    app_file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(app_file_handler)

    error_file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "errors.log", maxBytes=1024 * 1024 * 5, backupCount=3
    )
    error_file_handler.setFormatter(logging.Formatter(log_format))
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


logger = logging.getLogger("excelsior")
