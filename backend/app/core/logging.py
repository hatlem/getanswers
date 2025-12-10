"""Logging configuration for the application."""

import logging
import sys
import json
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development environment."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(environment: str = "development", log_level: str = "INFO") -> logging.Logger:
    """
    Setup application logging configuration.

    Args:
        environment: Application environment (development, production)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger instance for the application
    """
    # Get log level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Set formatter based on environment
    if environment == "production":
        # JSON format for production (better for log aggregation)
        formatter = JSONFormatter()
    else:
        # Human-readable format with colors for development
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = ColoredFormatter(log_format)

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)

    # Create application logger
    app_logger = logging.getLogger("getanswers")
    app_logger.setLevel(level)

    return app_logger


# Initialize logger (will be configured by main.py on startup)
logger = logging.getLogger("getanswers")


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any
) -> None:
    """
    Log a message with additional context.

    Args:
        logger: Logger instance
        level: Log level (logging.INFO, logging.ERROR, etc.)
        message: Log message
        **context: Additional context fields to include
    """
    extra = {k: v for k, v in context.items() if v is not None}
    logger.log(level, message, extra=extra)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    request_id: str = None,
    user_id: str = None
) -> None:
    """
    Log an HTTP request.

    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration: Request duration in seconds
        request_id: Optional request ID
        user_id: Optional user ID
    """
    log_with_context(
        logger,
        logging.INFO,
        f"{method} {path} {status_code} {duration:.3f}s",
        request_id=request_id,
        user_id=user_id,
        duration=duration
    )


def log_error(
    message: str,
    error: Exception = None,
    request_id: str = None,
    user_id: str = None,
    **context: Any
) -> None:
    """
    Log an error with context.

    Args:
        message: Error message
        error: Optional exception object
        request_id: Optional request ID
        user_id: Optional user ID
        **context: Additional context fields
    """
    extra = {
        "request_id": request_id,
        "user_id": user_id,
        **context
    }
    extra = {k: v for k, v in extra.items() if v is not None}

    if error:
        logger.error(message, exc_info=error, extra=extra)
    else:
        logger.error(message, extra=extra)
