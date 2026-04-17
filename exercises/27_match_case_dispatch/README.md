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

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

Read each `case` pattern carefully and compare it to the event shape the handler needs. Mapping patterns bind only the keys they mention; any field not in the pattern isn't captured.

Then look at the fallthrough: what does an unknown event type do today? Does that match what the test expects?

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. The `keypress` case captures `key` but not `modifiers`, then calls the handler with `modifiers=[]`. The event's modifiers are thrown away.
2. The `resize` case matches `{"type": "resize"}` with no other keys and returns a string that doesn't contain the dimensions.
3. The wildcard `case _: return None` is the bug Guide 10 warns about. Unknown events should raise, not silently produce None.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `case {"type": "keypress", "key": key, "modifiers": modifiers}: return describe_keypress(key, modifiers)`
2. `case {"type": "resize", "width": w, "height": h}: return describe_resize(w, h)`
3. `case _: raise ValueError(f"unknown event: {event!r}")`

</details>

## Discussion

For truly closed unions (a `Literal` or `Enum` of event types), `typing.assert_never` in the wildcard branch gives you mypy-level exhaustiveness: adding a new variant without handling it is flagged before the code ever runs. For open-ended input like JSON dicts, raising `ValueError` is the best you can do at runtime.

The solution walkthrough shows a version using dataclass-based events and `assert_never`, which would have made bugs 1 and 2 type-checkable too.

## Relevant reading

- `guides/10_paths_and_matching.py` — Sections 5–8 (match/case + assert_never)
