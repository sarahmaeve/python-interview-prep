# Exercise 27: match/case Dispatch

An event router that uses `match`/`case` to dispatch events to handlers. The implementation has **3 bugs** — all classic shapes of "the match statement looks right but doesn't actually handle what it claims to".

## How to run the tests

```bash
cd exercises/27_match_case_dispatch
python3 -m unittest test_event_router
```

Your goal is to edit `event_router.py` until all tests pass. Do **not** modify the test file.

## The supported events

```python
{"type": "click",   "x": int, "y": int}
{"type": "scroll",  "delta": int}
{"type": "keypress", "key": str, "modifiers": list[str]}
{"type": "resize",  "width": int, "height": int}
```

Unknown events must raise a clear error — they must **not** silently return `None`.

## Principle Primer

A mapping pattern binds only the keys it names; additional keys are allowed but
unnamed data is unavailable to the branch. Compare the data a handler needs
with the names its pattern captures. Also make the fallback contract explicit:
open-ended external input needs a deliberate runtime error or default rather
than accidental fallthrough.

If you get stuck, use [HINTS.md](HINTS.md).

## Discussion

For truly closed unions (a `Literal` or `Enum` of event types), `typing.assert_never` in the wildcard branch gives you mypy-level exhaustiveness: adding a new variant without handling it is flagged before the code ever runs. For open-ended input like JSON dicts, raising `ValueError` is the best you can do at runtime.

The solution walkthrough also explores dataclass-based events and
`assert_never`.

## Relevant reading

- `guides/10_paths_and_matching.py` — Sections 5–8 (match/case + assert_never)
