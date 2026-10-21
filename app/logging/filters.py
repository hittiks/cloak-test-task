import logging


class SuppressTracebackFilter(logging.Filter):
    """Filter that removes exception info from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Remove exception info to prevent traceback printing
        record.exc_info = None
        record.exc_text = None
        # Always return True to keep the log record
        return True
