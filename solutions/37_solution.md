# Solution: Exercise 37 — Package Imports

## Bugs Found

The three failures come from different layers of Python's import machinery:

1. **Import-time side effect** — `inventory_tool/__init__.py` prints whenever
   any part of the package is imported. Package initialization is unavoidable,
   so even `from inventory_tool.cli import main` produces unrelated output.
2. **Top-level versus package-relative import** —
   `inventory_tool/__main__.py` uses `from cli import main`. That asks Python
   for a top-level module named `cli`, not for the sibling module in
   `inventory_tool`.
3. **Circular runtime import created by an annotation** — `models` imports
   `Reporter`, while `reporting` imports `Inventory`. Whichever module is
   imported first asks the other for a class that has not been defined yet.

## Diagnosis Process

The subprocess tests matter here. A single test interpreter would retain
successfully imported modules in `sys.modules`, making import order harder to
observe. Each fresh process exposes the real startup behavior.

Read the shortest traceback from the bottom upward:

- `No module named 'cli'` shows that Python searched for a top-level name.
- `cannot import name ... from partially initialized module` identifies a
  cycle, not a missing file.
- Successful commands with an extra first line point to code executed as an
  import side effect.

For the cycle, write the chain down:

```text
models -> reporting -> models.Inventory (not defined yet)
reporting -> models -> reporting.Reporter (not defined yet)
```

Then classify each arrow. `reporting` constructs an `Inventory`, so that import
is needed at runtime. `models` mentions `Reporter` only in a type annotation,
so that dependency can remain visible to type checkers without running.

## The Fixes

Keep package initialization quiet:

```python
# inventory_tool/__init__.py
"""Inventory reporting package."""
```

Use package-relative syntax for the sibling entry point:

```python
# inventory_tool/__main__.py
from .cli import main

raise SystemExit(main())
```

Defer annotation evaluation and guard the type-only import:

```python
# inventory_tool/models.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .reporting import Reporter


@dataclass(frozen=True)
class Inventory:
    items: tuple[str, ...]

    def render(self, reporter: Reporter) -> str:
        return reporter.render(self)
```

`TYPE_CHECKING` is the constant `False` during normal execution, but static
analyzers treat that branch as active. With postponed annotations, Python does
not need to resolve `Reporter` while defining `Inventory`.

## Why Other Repairs Are Weaker

- Appending directories to `sys.path` inside the package makes behavior depend
  on filesystem layout and can silently import the wrong same-named module.
  Installation, `PYTHONPATH`, or a test runner should establish where the
  top-level package lives.
- Catching `ImportError` and trying both relative and absolute imports hides
  genuine failures inside the imported module and gives the package two
  identities depending on execution context.
- Moving imports inside every function may break the immediate cycle, but it
  obscures dependencies and repeats import work. A local import is reasonable
  when the dependency is genuinely optional or call-specific, not as the first
  response to a type-only edge.

## Discussion

- `python -m inventory_tool` asks the import system to locate
  `inventory_tool`, establishes its package context, and runs
  `inventory_tool.__main__`. Executing `inventory_tool/__main__.py` as a path
  treats it as a standalone `__main__` module, so it does not automatically
  have the same relative-import context.
- A larger cycle often signals misplaced ownership. If both modules truly need
  shared runtime types, extracting those types or a small `Protocol` into a
  third low-level module can produce a clearer dependency graph.
- Quiet imports make libraries composable. Network calls, logging
  configuration, command execution, and user-facing output belong behind
  explicit functions or entry points.
