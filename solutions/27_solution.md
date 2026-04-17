# Solution: Exercise 27 — match/case Dispatch

## Bugs Found

1. **The `keypress` case drops `modifiers`.** The pattern captures `key` but not the `modifiers` list, then calls the handler with `modifiers=[]`. Any event's actual modifiers are silently discarded.

2. **The `resize` case matches only on type.** `case {"type": "resize"}:` doesn't bind `width` or `height`, and the branch returns a hard-coded `"resized"` instead of delegating to `describe_resize`.

3. **The wildcard returns `None`.** Unknown events silently produce `None`, which propagates into downstream pipelines and causes mysterious failures far from the source.

## Diagnosis Process

- `test_modifiers_are_honored` fails because `"key: s"` comes back instead of `"key: ctrl+shift+s"`. Reading `handle_event`, the `keypress` case never captures `modifiers`, so the handler call uses `modifiers=[]`.
- `test_resize_carries_dimensions` fails with the literal string `"resized"`. The resize case pattern has no width/height bindings.
- `test_unknown_type_raises` expects `ValueError`; instead the dispatch silently returns `None`. The `case _:` branch is returning `None`.

## The Fix

```python
def handle_event(event: dict) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return describe_click(x, y)
        case {"type": "scroll", "delta": delta}:
            return describe_scroll(delta)
        case {"type": "keypress", "key": key, "modifiers": modifiers}:
            return describe_keypress(key, modifiers)
        case {"type": "resize", "width": w, "height": h}:
            return describe_resize(w, h)
        case _:
            raise ValueError(f"unknown event: {event!r}")
```

## Why This Bug Matters

`match`/`case` looks like `switch`/`default`, but with a crucial difference: *there is no runtime exhaustiveness check*. If you forget a case, execution falls through — and when the case uses a mapping pattern that only binds SOME keys, the others are silently discarded. Both bugs 1 and 2 are shapes of this: the pattern looks right, the code type-checks, but the handler is missing information.

Three defences, in order of strength:

1. **Bind every field the handler needs.** Mapping patterns only capture what you name — don't rely on "same dict is in scope". Always destructure explicitly.

2. **Raise on unknown events.** `case _: return None` is the shape Guide 10 Section 8 warns against. Either raise, or — if the caller expects `None` — make that explicit with a named sentinel.

3. **For truly closed unions, use `typing.assert_never`.** Switch from `dict` inputs to a closed discriminated union (dataclasses + `typing.assert_never`) and mypy verifies exhaustiveness before the code runs.

## Discussion — The Type-Safe Version

The dict-in, string-out pattern is idiomatic for JSON-shaped data. If the event types were modeled as dataclasses, the exhaustiveness check would be static:

```python
from dataclasses import dataclass
from typing import assert_never

@dataclass
class Click:    x: int; y: int
@dataclass
class Scroll:   delta: int
@dataclass
class Keypress: key: str; modifiers: list[str]
@dataclass
class Resize:   width: int; height: int

Event = Click | Scroll | Keypress | Resize

def handle_event(event: Event) -> str:
    match event:
        case Click(x, y):             return describe_click(x, y)
        case Scroll(delta):           return describe_scroll(delta)
        case Keypress(key, mods):     return describe_keypress(key, mods)
        case Resize(w, h):            return describe_resize(w, h)
        case _ as unhandled:
            assert_never(unhandled)   # mypy flags if a variant is missed
```

Add a new `Event` subtype and forget to add a `case` — mypy fails, and runtime raises `AssertionError` with a useful message.

`route_all`'s current `try/except Exception: pass` is another anti-pattern that crept through: it turns unknown events into silent drops instead of logging them. In real code you'd log the unknown-event case; for the test suite, dropping is fine.
