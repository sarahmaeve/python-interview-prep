"""
Guide 11 — Context Managers and Decorators
============================================
Run:  python guides/11_context_and_decorators.py

Two Python features that turn repetitive boilerplate into reusable pieces:

    Context managers  — the `with` protocol: guarantee cleanup even on error.
                        Two ways to write one:
                          __enter__/__exit__ methods on a class
                          @contextlib.contextmanager on a generator function

    Decorators        — functions that wrap other functions to add behaviour.
                        Must preserve the wrapped function's identity with
                        functools.wraps, or you break introspection, logging,
                        mocking, and docstrings.

Both show up in interview questions as "write a context manager for X" and
"what's wrong with this decorator?".  The bugs in exercises 28 and 31
mirror real production incidents.

TABLE OF CONTENTS
  1. The context manager protocol           (line ~35)
  2. Writing one as a class                 (line ~90)
  3. Writing one with @contextmanager       (line ~155)
  4. contextlib.suppress / ExitStack        (line ~215)
  5. Decorator basics                       (line ~270)
  6. Why functools.wraps matters            (line ~340)
  7. Decorators with arguments              (line ~400)
  8. Class-based decorators                 (line ~470)
"""

from __future__ import annotations

import functools
import io
import logging
import time
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager, suppress
from typing import Any, TypeVar


# ============================================================================
# 1. THE CONTEXT MANAGER PROTOCOL
# ============================================================================
#
# A context manager is any object that implements two methods:
#     __enter__(self)           — called when the `with` block starts.
#                                 Returns the value bound to `as`.
#     __exit__(self, exc_type, exc_val, exc_tb)
#                               — called when the block exits, even on
#                                 exception.  Return True to SWALLOW the
#                                 exception; return False/None to propagate.
#
# The point: RESOURCES ARE CLEANED UP EVEN IF THE BODY RAISES.  This is
# the whole reason `with` exists.  If you find yourself writing
# `try: ... finally: resource.close()`, reach for a context manager.


def demo_protocol() -> None:
    print("=" * 60)
    print("1. The context manager protocol")
    print("=" * 60)

    class Tracer:
        def __init__(self, label: str) -> None:
            self.label = label

        def __enter__(self) -> "Tracer":
            print(f"  [enter] {self.label}")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            if exc_type is None:
                print(f"  [exit]  {self.label}   (clean)")
            else:
                print(f"  [exit]  {self.label}   (raised {exc_type.__name__})")
            return False  # do not swallow the exception

    # Clean path.
    with Tracer("normal") as t:
        assert isinstance(t, Tracer)

    # Error path — __exit__ still runs.
    try:
        with Tracer("broken"):
            raise ValueError("boom")
    except ValueError:
        print("  (caller saw the ValueError because __exit__ returned False)")
    print()


# ============================================================================
# 2. WRITING ONE AS A CLASS
# ============================================================================
#
# Reach for a class-based context manager when your resource has state
# that multiple methods touch, or when you want to keep several __exit__
# overloads for subclasses.


class FileTimer:
    """Times a block of code and writes the timing to a file.

    Usage:
        with FileTimer(path) as ft:
            do_work()
        # path now contains "elapsed=0.123s"
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.start: float | None = None
        self.elapsed: float = 0.0

    def __enter__(self) -> "FileTimer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        assert self.start is not None
        self.elapsed = time.perf_counter() - self.start
        # Always record the elapsed time, even if the block raised.
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(f"elapsed={self.elapsed:.3f}s\n")
        return False  # propagate any exception


def demo_class_based() -> None:
    print("=" * 60)
    print("2. Class-based context manager")
    print("=" * 60)

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "timing.log"
        with FileTimer(str(log)) as ft:
            time.sleep(0.01)
        assert log.exists()
        assert ft.elapsed >= 0.01
        print(f"  elapsed recorded: {log.read_text().strip()}")
    print()


# ============================================================================
# 3. WRITING ONE WITH @contextmanager
# ============================================================================
#
# For simple cases, @contextlib.contextmanager is terser.  You write one
# generator function; everything before `yield` is __enter__, everything
# after is __exit__.
#
# If the body might raise, wrap the yield in try/finally so the cleanup
# runs on the error path too.  This is the #1 bug in exercise 28.


@contextmanager
def noisy_section(label: str) -> Iterator[str]:
    """Log entry and exit; cleanup runs even on exceptions."""
    logger = logging.getLogger("demo.noisy")
    logger.info("entering %s", label)
    try:
        yield label.upper()
    finally:
        # Without try/finally, a raise inside the `with` block would skip
        # this log line and leak the resource.
        logger.info("exiting  %s", label)


def demo_contextmanager_decorator() -> None:
    print("=" * 60)
    print("3. @contextmanager")
    print("=" * 60)

    # Hook up a logger for this demo.
    logger = logging.getLogger("demo.noisy")
    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setFormatter(logging.Formatter("    %(levelname)s: %(message)s"))
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    with noisy_section("alpha") as name:
        print(f"  inside with — name = {name}")

    # Error path: the `exiting` line must still appear.
    try:
        with noisy_section("beta"):
            raise RuntimeError("oops")
    except RuntimeError:
        pass

    print("  captured log output:")
    for line in buf.getvalue().rstrip("\n").split("\n"):
        print(line)
    print()


# ============================================================================
# 4. contextlib.suppress AND ExitStack
# ============================================================================
#
# Two utilities from contextlib that are worth memorizing:
#
#   suppress(*exceptions)
#     — a context manager that swallows the named exceptions.  Replaces
#       try/except/pass for the common "I don't care if this fails" case.
#
#   ExitStack
#     — lets you combine an unknown number of context managers at runtime.
#       Perfect when you have a list of files/connections to open dynamically.


def demo_suppress_and_exitstack() -> None:
    print("=" * 60)
    print("4. contextlib.suppress and ExitStack")
    print("=" * 60)

    # suppress: eats the exception type(s) you name.
    with suppress(FileNotFoundError):
        open("/no/such/file").read()
    print("  FileNotFoundError suppressed — no exception propagated")

    # ExitStack: open N things dynamically, clean them all up.
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        paths = [Path(td) / f"file_{i}.txt" for i in range(3)]
        for p in paths:
            p.write_text(f"hello {p.name}\n")

        with ExitStack() as stack:
            # Open all files as part of the stack.  Any exception in any
            # open() still cleans up everything that was already opened.
            handles = [stack.enter_context(p.open(encoding="utf-8")) for p in paths]
            print(f"  opened {len(handles)} files via ExitStack")
            total = sum(len(h.read()) for h in handles)
        # All handles closed here, no matter what happened inside.
        print(f"  total bytes read: {total}")
    print()


# ============================================================================
# 5. DECORATOR BASICS
# ============================================================================
#
# A decorator is a function that takes a function and returns a replacement.
# `@decorator` above a def is syntactic sugar for `func = decorator(func)`.

F = TypeVar("F", bound=Callable[..., Any])


def timing(func: F) -> F:
    """Log the elapsed wall time of each call."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        t0 = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - t0
            print(f"  [timing] {func.__name__} took {elapsed * 1000:.1f}ms")
    return wrapper  # type: ignore[return-value]


@timing
def slow_add(a: int, b: int) -> int:
    """Add two integers after a tiny sleep."""
    time.sleep(0.005)
    return a + b


def demo_decorator_basics() -> None:
    print("=" * 60)
    print("5. Decorator basics")
    print("=" * 60)

    result = slow_add(2, 3)
    assert result == 5
    print(f"  slow_add(2, 3) = {result}")

    # functools.wraps preserved the metadata:
    assert slow_add.__name__ == "slow_add"
    assert slow_add.__doc__ is not None and "Add two integers" in slow_add.__doc__
    print(f"  slow_add.__name__ = {slow_add.__name__!r}  (wraps preserved it)")
    print(f"  slow_add.__doc__  starts with {slow_add.__doc__[:20]!r}...")
    print()


# ============================================================================
# 6. WHY functools.wraps MATTERS
# ============================================================================
#
# Without functools.wraps, the wrapper REPLACES the original function's
# metadata.  Consequences:
#   - logger.exception shows "in wrapper" instead of the real function name
#   - Sphinx/pdoc documentation is empty (docstring gone)
#   - unittest.mock.patch("module.func") can fail if introspection relied
#     on __wrapped__ or signature
#   - Stack traces are harder to read
#
# It's a one-line fix and costs nothing.  ALWAYS use @functools.wraps(func)
# on the inner wrapper function.


def demo_why_wraps_matters() -> None:
    print("=" * 60)
    print("6. Why functools.wraps matters")
    print("=" * 60)

    def bad_decorator(func):
        # NOTE: no @functools.wraps here — the wrapper is anonymous.
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def good_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @bad_decorator
    def bad(name: str) -> str:
        """Greet someone."""
        return f"hello {name}"

    @good_decorator
    def good(name: str) -> str:
        """Greet someone."""
        return f"hello {name}"

    print(f"  bad.__name__  = {bad.__name__!r}   <- identity lost (it's 'wrapper')")
    print(f"  bad.__doc__   = {bad.__doc__!r}")
    print(f"  good.__name__ = {good.__name__!r}")
    print(f"  good.__doc__  = {good.__doc__!r}")

    # Key diagnostic for any "mock not patching what I think it is":
    # check the __wrapped__ attribute (only present when wraps was used).
    assert hasattr(good, "__wrapped__")
    assert not hasattr(bad, "__wrapped__")
    print(f"  good.__wrapped__ exists   : {hasattr(good, '__wrapped__')}")
    print(f"  bad.__wrapped__  exists   : {hasattr(bad, '__wrapped__')}   <- missing")
    print()


# ============================================================================
# 7. DECORATORS WITH ARGUMENTS
# ============================================================================
#
# A "decorator with arguments" is really two nested functions deep:
#
#     @retry(max_attempts=3)
#     def fetch(...): ...
#
# is shorthand for:
#
#     fetch = retry(max_attempts=3)(fetch)
#
# So retry(max_attempts=3) must RETURN a decorator, not be one directly.
# The outer layer captures the arguments; the inner layer is the usual
# func -> wrapper transform.


def retry(max_attempts: int, exceptions: tuple[type[BaseException], ...] = (Exception,)):
    """Retry *func* up to *max_attempts* times on listed exceptions."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: BaseException | None = None
            for _attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
            assert last_exc is not None
            raise last_exc
        return wrapper  # type: ignore[return-value]

    return decorator


_attempts = 0


@retry(max_attempts=3, exceptions=(ConnectionError,))
def flaky() -> str:
    global _attempts
    _attempts += 1
    if _attempts < 3:
        raise ConnectionError(f"attempt {_attempts}")
    return "ok"


def demo_parameterized_decorator() -> None:
    print("=" * 60)
    print("7. Decorators with arguments")
    print("=" * 60)

    global _attempts
    _attempts = 0
    result = flaky()
    assert result == "ok"
    assert _attempts == 3
    print(f"  @retry succeeded after {_attempts} attempts, result={result!r}")
    print()


# ============================================================================
# 8. CLASS-BASED DECORATORS
# ============================================================================
#
# If your decorator needs state (a call counter, a cache, a registry), a
# class is often clearer than nested functions.  Make it callable by
# defining __call__.


class CallCounter:
    """A decorator that counts how many times the wrapped function is called."""

    def __init__(self, func: Callable[..., Any]) -> None:
        functools.update_wrapper(self, func)   # class-decorator equivalent of @wraps
        self._func = func
        self.count = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.count += 1
        return self._func(*args, **kwargs)


@CallCounter
def greet(name: str) -> str:
    """Return a greeting."""
    return f"hi {name}"


def demo_class_decorator() -> None:
    print("=" * 60)
    print("8. Class-based decorators")
    print("=" * 60)

    greet("ada")
    greet("grace")
    greet("hopper")
    # The decorator *is* the callable now — state lives on it.
    assert greet.count == 3  # type: ignore[attr-defined]
    print(f"  greet.count = {greet.count}")
    print(f"  greet.__name__ = {greet.__name__!r}   (via update_wrapper)")
    print()


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    demo_protocol()
    demo_class_based()
    demo_contextmanager_decorator()
    demo_suppress_and_exitstack()
    demo_decorator_basics()
    demo_why_wraps_matters()
    demo_parameterized_decorator()
    demo_class_decorator()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. `with` guarantees cleanup even on exceptions.  Any time you'd")
    print("     write try/finally around a resource, use a context manager.")
    print("  2. @contextlib.contextmanager + yield is the quickest way to")
    print("     write one.  Wrap the yield in try/finally.")
    print("  3. ALWAYS use @functools.wraps on decorator wrappers.  One line.")
    print("     Saves you from debugging 'mock isn't patching' / 'docstring")
    print("     missing' / unreadable tracebacks later.")
    print("  4. Decorators-with-arguments are three nested functions.  The")
    print("     outermost captures arguments and returns the real decorator.")
    print()
    print("  Next up:")
    print("    Exercise 28 — Context Manager Leaks  (missing try/finally)")
    print("    Exercise 31 — Decorator @wraps        (forgotten wraps + bugs)")
    print()


if __name__ == "__main__":
    main()
