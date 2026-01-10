import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def setup_logger(
    log_dir: Path,
    debug: bool = False,
    name: str = "sec_pipeline",
) -> logging.Logger:
    """
    Create a structured JSON logger with console + file handlers.
    """

    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False

    # Clear existing handlers (important in notebooks / reruns)
    if logger.handlers:
        logger.handlers.clear()

    # ---- File handler (JSON, full detail) ----
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{name}_{timestamp}.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload: Dict[str, Any] = {
                "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "line": record.lineno,
            }

            # Attach structured extras safely
            for key, value in record.__dict__.items():
                if key.startswith("_"):
                    continue
                if key in payload or key in (
                    "args", "msg", "levelname", "levelno",
                    "pathname", "filename", "exc_info",
                    "exc_text", "stack_info", "created",
                    "msecs", "relativeCreated", "thread",
                    "threadName", "processName", "process",
                    "name", "module", "lineno",
                ):
                    continue

                try:
                    json.dumps(value)
                    payload[key] = value
                except Exception:
                    payload[key] = str(value)

            return json.dumps(payload, ensure_ascii=False)

    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    # ---- Console handler (human-readable) ----
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-5s | %(message)s",
            "%H:%M:%S",
        )
    )
    logger.addHandler(console_handler)

    logger.info(
        "Logger initialized",
        extra={
            "debug": debug,
            "log_file": str(log_file),
        },
    )

    return logger
