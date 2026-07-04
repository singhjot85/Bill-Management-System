# logging_config.py
import logging
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR_PATH = os.getenv("LOG_DIR_PATH", str(BASE_DIR / "logs"))
FILTER_SENSITIVE_DATA = os.getenv("FILTER_SENSITIVE_DATA", True)
FILTER_HEALTH_CHECKS = os.getenv("FILTER_HEALTH_CHECK_LOGS", True)

# Create logs directory if it doesn't exist
LOG_DIR = Path(LOG_DIR_PATH)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# Log format configurations
class LogFormats:
    """Centralized log format definitions"""

    STANDARD = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    VERBOSE = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    JSON = "%(asctime)s - %(levelname)s - %(name)s - %(message)s - %(pathname)s"
    SIMPLE = "%(asctime)s - %(levelname)s - %(message)s"
    ERROR = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s - %(exc_info)s"


# Sensitive data filtering
class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive information in logs"""

    SENSITIVE_KEYS = {
        "password",
        "passwd",
        "secret",
        "token",
        "key",
        "auth",
        "authorization",
        "api_key",
        "apikey",
        "credit_card",
        "cc_number",
        "cvv",
        "ssn",
        "access_token",
        "refresh_token",
        "private_key",
    }

    def filter(self, record):
        # Mask sensitive data in message
        if not FILTER_SENSITIVE_DATA:
            return True

        for key in self.SENSITIVE_KEYS:
            if key in str(record.msg):
                record.msg = str(record.msg).replace(f"{key}=", f"{key}=[MASKED]")
        return True


class HealthCheckFilter(logging.Filter):
    """Filter out health check endpoints to reduce noise"""

    HEALTH_PATHS = ["/health", "/ping", "/readiness", "/liveness"]

    def filter(self, record):
        if not FILTER_HEALTH_CHECKS:
            return True

        if hasattr(record, "path"):
            if any(path in str(record.path) for path in self.HEALTH_PATHS):
                return False
        return True


# Custom logging levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


# Console color codes for development
class ConsoleColors:
    """ANSI color codes for console logging"""

    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        "DEBUG": ConsoleColors.BLUE,
        "INFO": ConsoleColors.GREEN,
        "WARNING": ConsoleColors.YELLOW,
        "ERROR": ConsoleColors.RED,
        "CRITICAL": ConsoleColors.MAGENTA,
    }

    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, ConsoleColors.WHITE)
        return f"{color}{log_message}{ConsoleColors.RESET}"


def get_logging_config(debug=False, log_level="INFO"):
    """
    Generate production-grade logging configuration

    Args:
        debug: Boolean to enable debug mode
        log_level: String for log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        dict: Logging configuration dictionary
    """

    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)

    # Determine environment
    is_production = os.getenv("DJANGO_ENV", "production") == "production"
    is_development = not is_production or debug

    # Default handlers
    handlers = ["console"]

    # Add file handlers for production
    if is_production:
        handlers.extend(["file_info", "file_error", "file_json"])

    # Add performance logging
    if is_development:
        handlers.append("file_performance")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sensitive": {
                "()": SensitiveDataFilter,
            },
            "health_check": {
                "()": HealthCheckFilter,
            },
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "formatters": {
            "standard": {
                "format": LogFormats.STANDARD,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "verbose": {
                "format": LogFormats.VERBOSE,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": LogFormats.SIMPLE,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "error": {
                "format": LogFormats.ERROR,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": "%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "colored": {
                "()": ColoredConsoleFormatter,
                "format": LogFormats.VERBOSE,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "colored" if is_development else "standard",
                "filters": ["sensitive", "health_check"],
                "level": logging.DEBUG if is_development else logging.INFO,
            },
            "file_info": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "info.log",
                "maxBytes": 50 * 1024 * 1024,  # 50MB
                "backupCount": 10,
                "formatter": "standard",
                "filters": ["sensitive", "health_check"],
                "level": logging.INFO,
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "error.log",
                "maxBytes": 50 * 1024 * 1024,  # 50MB
                "backupCount": 20,
                "formatter": "error",
                "filters": ["sensitive"],
                "level": logging.ERROR,
            },
            "file_json": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "app.log.json",
                "maxBytes": 100 * 1024 * 1024,  # 100MB
                "backupCount": 5,
                "formatter": "json",
                "filters": ["sensitive"],
                "level": level,
            },
            "file_performance": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "performance.log",
                "maxBytes": 20 * 1024 * 1024,  # 20MB
                "backupCount": 5,
                "formatter": "verbose",
                "filters": ["sensitive"],
                "level": logging.DEBUG,
            },
            "mail_admins": {
                "class": "django.utils.log.AdminEmailHandler",
                "filters": ["require_debug_false", "sensitive"],
                "level": "ERROR",
                "include_html": True,
            },
        },
        "loggers": {
            # Root logger
            "": {
                "handlers": handlers,
                "level": level,
                "propagate": True,
            },
            # Django core loggers
            "django": {
                "handlers": ["console", "file_info"],
                "level": logging.INFO if is_production else logging.DEBUG,
                "propagate": False,
            },
            "django.request": {
                "handlers": ["console", "file_error", "mail_admins"],
                "level": logging.ERROR,
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["console"],
                "level": logging.WARNING,
                "propagate": False,
            },
            "django.security": {
                "handlers": ["console", "file_error"],
                "level": logging.WARNING,
                "propagate": False,
            },
            # Application loggers
            "app": {
                "handlers": ["console", "file_info", "file_error"],
                "level": level,
                "propagate": True,
            },
            "api": {
                "handlers": ["console", "file_info", "file_error"],
                "level": level,
                "propagate": True,
            },
            "services": {
                "handlers": ["console", "file_info", "file_error"],
                "level": level,
                "propagate": True,
            },
            # Third-party loggers
            "celery": {
                "handlers": ["console", "file_info", "file_error"],
                "level": logging.WARNING,
                "propagate": False,
            },
            "requests": {
                "handlers": ["console"],
                "level": logging.WARNING,
                "propagate": False,
            },
            "urllib3": {
                "handlers": ["console"],
                "level": logging.WARNING,
                "propagate": False,
            },
        },
    }

    return config
