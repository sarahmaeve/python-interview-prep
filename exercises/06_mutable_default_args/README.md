# Exercise 06: Mutable Default Arguments — Event Logger

An event logging system lets you create `Event` objects and collect them in an
`EventLogger`. The implementation looks straightforward, but it hides 3 bugs
related to mutable state.

The **tests are correct**. The **implementation has 3 bugs**. Read the tests,
understand the expected behavior, then fix `event_logger.py`.

## Classes

| Class / Method | Purpose |
|---|---|
| `Event(name, timestamp, tags)` | Represents a single event. `timestamp` defaults to current time; `tags` defaults to an empty list. |
| `EventLogger.log_event(event)` | Stores an event. |
| `EventLogger.get_events_by_tag(tag)` | Returns a list of events that have the given tag. |
| `EventLogger.get_summary()` | Returns a dict mapping each tag to the number of events with that tag. |

## How to work through this exercise

1. Run the tests: `python3 -m unittest test_event_logger`
2. Read each failing test — they describe the correct behavior.
3. Find and fix the 3 bugs in `event_logger.py`.
4. Re-run until all 12 tests pass.

There are exactly **3 bugs** to find.
