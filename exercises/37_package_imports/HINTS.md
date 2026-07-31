# Hints: Exercise 37 — Package Imports

These hints become progressively more specific. Start with the first section
and rerun the tests before revealing the next.

## Hint 1: Diagnose the processes

Treat each symptom independently. Inspect the subprocess's stderr, then draw
the import chain that led there. Also distinguish output produced by the
requested command from output produced merely by loading the package.

Useful questions:

- Which directory is Python searching for a top-level package?
- Which module is executing when the unexpected output appears?
- In a circular-import traceback, which requested name has not been defined
  yet?

## Hint 2: Classify the dependencies

1. Package initialization should establish API and metadata, not announce that
   it happened.
2. The module entry point asks for a sibling as though it were a top-level
   module. These forms answer different questions:

   ```python
   from helper import run       # find a top-level module named helper
   from .helper import run      # find helper next to the current module
   ```

3. Follow the traceback between `models` and `reporting`. One direction needs a
   class at runtime; the other only needs a name for an annotation.

## Hint 3: Specific edits

1. Remove the output-producing statement from `inventory_tool/__init__.py`.
2. In `inventory_tool/__main__.py`, import the sibling with
   `from .cli import main`.
3. In `models.py`, add `from __future__ import annotations`, import
   `TYPE_CHECKING`, and put the `Reporter` import inside
   `if TYPE_CHECKING:`. Leave the runtime `Inventory` import in `reporting.py`.

The complete walkthrough is in
[solutions/37_solution.md](../../solutions/37_solution.md).
