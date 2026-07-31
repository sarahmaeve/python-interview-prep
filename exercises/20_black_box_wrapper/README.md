# Exercise 20: Black Box Module Wrapper

A quirky encoder module is provided as a **"black box"** — you may NOT modify `quirky_encoder.py`. Your job is to fix the `SafeEncoder` wrapper in `safe_encoder.py` that normalizes its behavior.

**This exercise practices:** introspection (`dir()`, `help()`, `repr()`), the adapter pattern, and defensive coding around unreliable dependencies.

## How to run the tests

```bash
cd exercises/20_black_box_wrapper
python -m unittest test_safe_encoder
```

Your goal: edit `safe_encoder.py` until all tests pass. Do **not** modify `quirky_encoder.py`.

## Exploration Tips

Before diving into the bugs, explore the black box in a Python REPL:

```python
from quirky_encoder import QuirkyEncoder
e = QuirkyEncoder()
dir(e)          # what methods and attributes are available?
help(e.encode)  # what does the docstring say?
repr(e)         # what internal state is visible?
e.encode(["a", "b", "c"])  # what does the output look like?
e.decode(e.encode(["Hello", "World"]))  # is round-trip clean?
```

## Files

| File | Role | Modify? |
|------|------|---------|
| `quirky_encoder.py` | Black box module | **NO** |
| `safe_encoder.py` | Wrapper (has 3 bugs) | **YES** |
| `test_safe_encoder.py` | Tests for the wrapper | NO |

## Principle Primer

An adapter owns the boundary between an unreliable dependency and a stable
application contract. Explore the dependency empirically, document what it
actually does, and normalize quirks in one place. Avoid exposing dependency
state or delegating through behavior known to retain state across calls.

There are 3 bugs. If you get stuck, use [HINTS.md](HINTS.md).
