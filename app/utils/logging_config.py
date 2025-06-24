"""
Logging configuration for the Trunk8 application.

This module provides centralized logging configuration with support for
different log levels, file and console output, and environment-based
configuration.
"""

import logging
import os
from typing import Optional


def setup_logging(
    app_name: str = "trunk8", log_level: Optional[str] = None
) -> logging.Logger:
    """
    Setup application logging with configurable log level.

    Args:
        app_name: Name of the application logger
        log_level: Log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  If None, uses TRUNK8_LOG_LEVEL environment variable or defaults to INFO

    Returns:
        logging.Logger: Configured logger instance
    """
    # Determine log level
    if log_level is None:
        log_level = os.environ.get("TRUNK8_LOG_LEVEL", "INFO").upper()

    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        print(f"Warning: Invalid log level '{log_level}', defaulting to INFO")
        log_level = "INFO"

    # Get numeric log level
    numeric_level = getattr(logging, log_level)

    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Log the logging configuration
    logger.info(f"Logging configured with level: {log_level}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f"trunk8.{name}")
