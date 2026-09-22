"""
NEXUS Logging Configuration.

Provides structured JSON logging to file and rich console output.
Every log entry includes optional simulation context (sim_id, round, agent).
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional


class NexusJsonFormatter(logging.Formatter):
    """Emits structured JSON log records for file output."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Optional simulation context
        for field in ("sim_id", "round", "agent_name"):
            value = getattr(record, field, None)
            if value is not None:
                log_entry[field] = value

        # Exception info
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> None:
    """
    Configure root logger with console + optional file output.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional path for JSON log file output.
    """
    root_logger = logging.getLogger("nexus")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler — use Rich if available, else plain
    try:
        from rich.logging import RichHandler

        console_handler = RichHandler(
            level=level,
            show_time=True,
            show_path=False,
            markup=True,
        )
    except ImportError:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    root_logger.addHandler(console_handler)

    # File handler — structured JSON
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(NexusJsonFormatter())
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger under the 'nexus' namespace.

    Args:
        name: Logger name (e.g. 'layer1.enterprise').

    Returns:
        Configured logging.Logger instance.
    """
    return logging.getLogger(f"nexus.{name}")
