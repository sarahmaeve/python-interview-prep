"""Event router — contains 3 bugs in match/case dispatch.

A small dispatcher that takes JSON-shaped event dicts and routes each
event to the correct handler.  The supported events are:

    {"type": "click",   "x": int, "y": int}
    {"type": "scroll",  "delta": int}
    {"type": "keypress", "key": str, "modifiers": list[str]}
    {"type": "resize",  "width": int, "height": int}

Handlers return a summary string.  Unknown events must be rejected
with a clear error — they must NOT silently fall through and produce
None.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading: guides/10_paths_and_matching.py Sections 5–8.
"""

from __future__ import annotations


def handle_event(event: dict) -> str:
    """Dispatch *event* to the matching handler and return its summary."""
    match event:
        case {"type": "click", "x": x, "y": y}:
            return describe_click(x, y)
        case {"type": "scroll", "delta": delta}:
            return describe_scroll(delta)
        case {"type": "keypress", "key": key}:
            return describe_keypress(key, modifiers=[])
        case {"type": "resize"}:
            return "resized"
        case _:
            return None  # type: ignore[return-value]


def describe_click(x: int, y: int) -> str:
    return f"click at ({x}, {y})"


def describe_scroll(delta: int) -> str:
    if delta < 0:
        return f"scroll up by {-delta}"
    return f"scroll down by {delta}"


def describe_keypress(key: str, modifiers: list[str]) -> str:
    if not modifiers:
        return f"key: {key}"
    return f"key: {'+'.join(sorted(modifiers))}+{key}"


def describe_resize(width: int, height: int) -> str:
    return f"resized to {width}x{height}"


def route_all(events: list[dict]) -> list[str]:
    """Route every event; drop any that can't be routed (logs omitted)."""
    results = []
    for ev in events:
        try:
            results.append(handle_event(ev))
        except Exception:
            pass
    return results
