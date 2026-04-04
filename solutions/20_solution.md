# Solution: Exercise 20 — Black Box Module Wrapper

## Exploration

Before touching `safe_encoder.py`, explore the black box in a REPL:

```python
from quirky_encoder import QuirkyEncoder
e = QuirkyEncoder()

repr(e)                        # QuirkyEncoder(separator='|') — reveals the separator
e.encode(["a", "b", "c"])     # 'a|b|c|' — trailing separator!
e.decode("Hello|World")       # ['hello', 'world'] — lowercased!
e.encode([None])              # 'None|' — None silently becomes "None"

# Mutable default in batch_encode:
e.batch_encode([["x"]])       # ['x|']
e.batch_encode([["y"]])       # ['x|', 'y|'] — contamination!
```

These quirks tell you what the wrapper must compensate for.

## Bugs Found

### Bug 1 — Inverted None check

**Location:** `safe_encoder.py`, `encode()` method

```python
# Before (raises on VALID fields, lets None through)
for field in fields:
    if field is not None:
        raise TypeError(...)

# After
for field in fields:
    if field is None:
        raise TypeError(...)
```

**Why it matters:** An inverted condition is one of the most common bugs in defensive checks. The tests make this obvious — `test_encode_accepts_strings` fails with TypeError on `["hello", "world"]`.

### Bug 2 — Trailing separator not stripped

**Location:** `safe_encoder.py`, `encode()` method

```python
# Before (returns "a|b|c|")
result = self._encoder.encode(fields)
return result

# After (returns "a|b|c")
result = self._encoder.encode(fields)
return result.rstrip(self._separator)
```

**Why it matters:** The wrapper's job is to normalize quirky behavior. The black box always appends a trailing separator — the wrapper must strip it.

### Bug 3 — Mutable default leaks through batch_encode

**Location:** `safe_encoder.py`, `batch_encode()` method

```python
# Before (delegates to black box, leaking its mutable default)
def batch_encode(self, records):
    return self._encoder.batch_encode(records)

# After (builds batch using the fixed encode method)
def batch_encode(self, records):
    return [self.encode(record) for record in records]
```

**Why it matters:** The black box's `batch_encode` has a mutable default `_accumulator=[]` that persists across calls. By building the batch using `self.encode()` instead, the wrapper avoids the contamination entirely. This is the adapter pattern in action — sometimes you can't use the black box's method at all.

## Key Insight: decode and case preservation

The `test_decode_preserves_case` test reveals that the black box's `decode()` lowercases everything. The wrapper's `decode()` correctly splits the string manually instead of delegating to the black box. This was already correct in the buggy code — but it's the kind of decision you'd need to make when wrapping a real opaque dependency.
