import logging
import sys
from pathlib import Path

# Create logs directory in the project root to avoid reload loops
LOGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def setup_logging():
    # Define the log format
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configure the root logger
    logging.basicConfig(
        level=logging.ERROR,
        format=log_format,
        handlers=[
            # Console output
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                LOGS_DIR / "app.log", maxBytes=1024 * 1024 * 10, backupCount=5
            ),
        ],
    )

    # You can further silence noisy third-party loggers here
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Initialize a global logger for this module
logger = logging.getLogger("excelsior")
