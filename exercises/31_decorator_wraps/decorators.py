"""Decorators — contains 3 bugs around decorator discipline.

Three common-shape decorators:

  - @log_calls      — logs entry and exit of each call
  - @retry(n)       — retries on exception up to n times
  - @count_calls    — class-based decorator that tracks call count

All three have bugs: one about introspection, one about argument
handling, one about state.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading: guides/11_context_and_decorators.py Sections 5–8.
"""

from __future__ import annotations

import functools
import logging
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. @log_calls — logs entry and exit of each call.
# ---------------------------------------------------------------------------


def log_calls(func):
    """Log an INFO message on each call."""
    def wrapper(*args, **kwargs):
        logger.info("calling %s", func.__name__)
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            logger.info("%s raised %s", func.__name__, type(exc).__name__)
            raise
        logger.info("%s returned", func.__name__)
        return result
    return wrapper


# ---------------------------------------------------------------------------
# 2. @retry(n) — retries on exception up to n times.
# ---------------------------------------------------------------------------


def retry(max_attempts: int):
    """Retry the decorated function on any Exception."""

    @functools.wraps(max_attempts)
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
            assert last_exc is not None
            raise last_exc
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# 3. @count_calls — a class-based decorator that counts calls.
# ---------------------------------------------------------------------------


class count_calls:
    """Count how many times the DECORATED function is called.

    Each function decorated with @count_calls keeps its OWN count — two
    functions decorated separately must not share a counter.

    The count is accessible via the decorated function's `.count` attribute.
    """

    _count = 0

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self._func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        count_calls._count += 1
        return self._func(*args, **kwargs)

    @property
    def count(self) -> int:
        return count_calls._count
