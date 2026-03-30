"""
Orin.LAB · Logger
Centralized structured logging with Rich formatting.
"""

import logging
import os
from rich.logging import RichHandler
from rich.console import Console

console = Console()

_loggers: dict[str, logging.Logger] = {}


def get_logger(name: str = "orinlab") -> logging.Logger:
    """Return a named logger, creating it once and caching it."""
    if name in _loggers:
        return _loggers[name]

    level = os.getenv("LOG_LEVEL", "INFO").upper()

    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True,
    )

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.addHandler(handler)
    logger.propagate = False

    _loggers[name] = logger
    return logger