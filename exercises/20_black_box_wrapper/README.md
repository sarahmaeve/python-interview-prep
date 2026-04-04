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

## Bugs: 3

<details>
<summary>Hint 1 (gentle)</summary>

Try encoding `["a", "b", "c"]` with the black box directly. Look at the last character of the result. Then try decoding what you just encoded — is the round-trip clean?
</details>

<details>
<summary>Hint 2 (moderate)</summary>

Read the `encode()` method in `safe_encoder.py` carefully. The None-rejection check has an inverted condition — it raises on valid values and lets None through. Also, the method returns the black box's raw output without cleaning it up.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **Trailing separator**: `encode()` returns the black box's output as-is, which always has a trailing separator (e.g., `"a|b|c|"`). Strip it with `result.rstrip(self._separator)` or `result[:-1]`.

2. **Inverted None check**: The condition `if field is not None` raises for valid fields. It should be `if field is None`.

3. **Mutable default contamination**: `batch_encode()` delegates directly to `self._encoder.batch_encode(records)`, which has a mutable default argument that accumulates across calls. Instead, build the batch by calling `self.encode()` on each record individually: `return [self.encode(record) for record in records]`.
</details>
