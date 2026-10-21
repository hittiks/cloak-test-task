import logging
import logging.config
import os

from app.config import settings


def get_base_logging_config(app_name: str) -> dict:
    """
    Get base logging configuration with formatters, filters, and handlers.

    Args:
        app_name: Name of the application (e.g., 'bot', 'api', 'prefect')
                 Used for log file paths: logs/<app_name>/logs.log

    Returns:
        Base logging configuration dictionary
    """
    log_dir = f"logs/{app_name}"
    log_file = f"{log_dir}/logs.log"
    error_log_file = f"{log_dir}/errors.log"

    if settings.DEBUG:
        level = "DEBUG"
    else:
        level = "INFO"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "custom": {
                "()": "app.logging.formatters.ColorizedFormatter",
                "fmt": "%(asctime)s | %(levelprefix)s | %(funcName)s | %(message)s",
                "use_colors": True,
            },
        },
        "filters": {
            "suppress_traceback": {
                "()": "app.logging.filters.SuppressTracebackFilter",
            },
        },
        "handlers": {
            "console": {
                "formatter": "custom",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": level,
            },
            "file": {
                "class": "logging.handlers.WatchedFileHandler",
                "level": "DEBUG",
                "formatter": "custom",
                "filename": log_file,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.WatchedFileHandler",
                "level": "ERROR",
                "formatter": "custom",
                "filename": error_log_file,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "httpx": {
                "handlers": ["console", "file", "error_file"],
                "level": "WARNING",
                "propagate": False,
            },
            "asyncio": {
                "handlers": ["console", "file", "error_file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }


def merge_logging_configs(base_config: dict, additional_config: dict) -> dict:
    """
    Merge additional logging configuration into base configuration.

    Args:
        base_config: Base logging configuration
        additional_config: Additional configuration to merge (formatters, handlers, loggers)

    Returns:
        Merged logging configuration
    """
    merged = base_config.copy()

    # Merge formatters
    if "formatters" in additional_config:
        merged["formatters"].update(additional_config["formatters"])

    # Merge filters
    if "filters" in additional_config:
        merged["filters"].update(additional_config["filters"])

    # Merge handlers
    if "handlers" in additional_config:
        merged["handlers"].update(additional_config["handlers"])

    # Merge loggers
    if "loggers" in additional_config:
        merged["loggers"].update(additional_config["loggers"])

    return merged


def setup_logging(
    app_name: str = "app",
    additional_config: dict | list[dict] | None = None,
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        app_name: Name of the application component (e.g., 'bot', 'api', 'prefect')
                 Used for log file paths: logs/<app_name>/logs.log
        additional_config: Optional additional logging configuration(s) to merge with base config.
                          Can be a single dict or a list of dicts. Multiple configs are merged
                          sequentially in the order provided.
                          Should contain formatters, handlers, and/or loggers.

    Example:
        # Simple setup for basic app
        setup_logging(app_name="bot")

        # With single additional config
        setup_logging(
            app_name="bot",
            additional_config={
                "handlers": {...},
                "loggers": {...}
            }
        )

        # With multiple additional configs
        setup_logging(
            app_name="bot",
            additional_config=[
                {"handlers": {...}},
                {"loggers": {...}},
                {"formatters": {...}}
            ]
        )
    """
    # Ensure logs directory exists
    log_dir = f"logs/{app_name}"
    os.makedirs(log_dir, exist_ok=True)

    # Get base configuration
    config = get_base_logging_config(app_name)

    # Merge with additional configuration(s) if provided
    if additional_config:
        # Support both single dict and list of dicts for backward compatibility
        configs_to_merge = (
            additional_config
            if isinstance(additional_config, list)
            else [additional_config]
        )
        for cfg in configs_to_merge:
            config = merge_logging_configs(config, cfg)

    # Apply logging configuration
    logging.config.dictConfig(config)
