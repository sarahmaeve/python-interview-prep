from datetime import datetime


class LogEntry:
    """A single parsed log entry.

    Attributes:
        timestamp (datetime): When the event occurred.
        level (str): The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        message (str): The log message text.
    """

    def __init__(self, timestamp, level, message):
        pass

    def __repr__(self):
        """Return a developer-friendly string representation.

        Format: LogEntry(LEVEL, 'message truncated to 40 chars...')
        """
        pass


def parse_line(line):
    """Parse a single log line into a LogEntry.

    Expected format: [TIMESTAMP] LEVEL: message

    Returns a LogEntry on success, or None if the line is malformed.
    Does not raise exceptions for bad input.

    Args:
        line: A string, potentially a valid log line.

    Returns:
        A LogEntry, or None if the line cannot be parsed.
    """
    pass


def parse_log(text):
    """Parse a multi-line log string into a list of LogEntry objects.

    Malformed lines are silently skipped.

    Args:
        text: A string containing one log line per line.

    Returns:
        A list of LogEntry objects, in the order they appeared.
    """
    pass


def filter_by_level(entries, min_level="DEBUG"):
    """Return entries at or above the given severity level.

    Severity order (lowest to highest): DEBUG < INFO < WARNING < ERROR < CRITICAL

    Args:
        entries: A list of LogEntry objects.
        min_level: The minimum level to include (default: "DEBUG", which
                   includes everything).

    Raises ValueError if min_level is not a recognized level.

    Returns:
        A list of LogEntry objects whose level is >= min_level in severity.
    """
    pass


def entries_between(entries, start, end):
    """Return entries whose timestamp falls within [start, end] inclusive.

    Args:
        entries: A list of LogEntry objects.
        start: A datetime — the earliest timestamp to include.
        end: A datetime — the latest timestamp to include.

    Returns:
        A list of LogEntry objects within the time range.
    """
    pass


def count_by_level(entries):
    """Return a dict mapping each log level to its count.

    Only levels that appear in the entries are included in the result.

    Args:
        entries: A list of LogEntry objects.

    Returns:
        A dict like {"ERROR": 5, "INFO": 12, ...}.
    """
    pass


