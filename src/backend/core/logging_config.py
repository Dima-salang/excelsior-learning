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

    # Root logger configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                LOGS_DIR / "app.log", maxBytes=1024 * 1024 * 10, backupCount=5
            ),
            logging.handlers.RotatingFileHandler(
                LOGS_DIR / "errors.log", maxBytes=1024 * 1024 * 5, backupCount=3
            ),
        ],
    )

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # Ensure our app loggers show errors
    logging.getLogger("excelsior").setLevel(logging.DEBUG)
    logging.getLogger("excelsior.llm").setLevel(logging.DEBUG)


class DetailedErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR


logger = logging.getLogger("excelsior")
