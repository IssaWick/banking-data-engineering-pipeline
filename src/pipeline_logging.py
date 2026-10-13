
import logging
from pathlib import Path


def configure_logging(log_file: Path) -> logging.Logger:
    """Configure console and file logging for pipeline execution."""

    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("banking_pipeline")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Prevent duplicate messages when the pipeline runs repeatedly.
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
