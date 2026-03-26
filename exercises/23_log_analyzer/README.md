# Exercise 23: Log Analyzer

## Difficulty: Intermediate

## Context

You are building a log analysis tool that parses application log lines, extracts
structured data, and computes summary statistics.

This exercise practices: systematic problem-solving, string parsing, error
handling, edge cases, defensive coding.

## Problem

Implement all the functions and the class in `log_analyzer.py`. Each has a
docstring describing its contract — read them carefully before writing any code.

## Constraints

- Log lines follow this format: `[TIMESTAMP] LEVEL: message`
  (e.g., `[2026-03-25T10:30:00] ERROR: Connection refused`)
- TIMESTAMP is ISO 8601 format
- LEVEL is one of: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Malformed lines must be skipped silently — do not crash the analyzer
- No external libraries (use `datetime.fromisoformat` for timestamp parsing)

## Instructions

1. Open `log_analyzer.py` and read every docstring.
2. Implement each function/method. Start with `LogEntry`, then `parse_line`,
   then the rest in order.
3. There are no pre-written tests. As you implement each function, consider
   what edge cases to test:
   - Empty input
   - Malformed lines (missing brackets, unknown level, bad timestamp)
   - `filter_by_level` with an unknown `min_level`
   - `entries_between` with timestamps exactly on the boundary

## Running your own tests

```bash
cd exercises/23_log_analyzer
python3 -m unittest discover -v   # run any test files you create
python3 -c "import log_analyzer"  # quick import smoke-check
```

## Hints (try without these first)

<details>
<summary>Hint 1 — parse_line structure</summary>
The format is <code>[TIMESTAMP] LEVEL: message</code>. Consider splitting on
<code>"] "</code> to separate the timestamp from the rest, then splitting the
remainder on <code>": "</code> with <code>maxsplit=1</code> to isolate the level
and message. Wrap the whole function in a try/except so a bad line returns None.
</details>

<details>
<summary>Hint 2 — filter_by_level ordering</summary>
Define a list or dict that maps level names to numeric ranks
(<code>DEBUG=0, INFO=1, ...</code>). Then compare ranks rather than strings.
Treat an unknown <code>min_level</code> argument however you like, but document
your choice.
</details>

