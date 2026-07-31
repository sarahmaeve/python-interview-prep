# Exercise 35: Debugging with pdb

An inventory audit pipeline (`inventory_audit.py`) has **3 bugs** that are easy
to gloss over while reading. The point of this exercise is the *method*: find
where the data first becomes wrong with the debugger, not with `print()`.

**This exercise practices:** `breakpoint()` and pdb fluency — stepping, inspecting, and watching state change — which is what "debug unfamiliar code live" looks like in an interview screen-share.

## How to run the tests

```bash
cd exercises/35_debugging_with_pdb
python3 -m unittest test_inventory_audit -v
```

## pdb crash course (5 minutes)

Drop into the debugger by adding one line where you want to stop:

```python
breakpoint()        # Python 3.7+; remove it when you're done
```

Then run the *one failing test* you're chasing:

```bash
python3 -m unittest test_inventory_audit.TestParseRows.test_parses_all_rows
```

The commands you'll use constantly:

| Command | Meaning |
|---|---|
| `n` | next — execute the current line, stay in this function |
| `s` | step — like `n`, but descend INTO function calls |
| `p expr` | print an expression (`p rows`, `p row["qty"]`) |
| `pp expr` | pretty-print (better for lists of dicts) |
| `w` | where — show the call stack |
| `u` / `d` | move up/down the stack to inspect a caller's variables |
| `b 42` | set a breakpoint at line 42 (`b func` works too) |
| `c` | continue until the next breakpoint |
| `q` | quit |

Two more tools worth knowing:

- **Post-mortem**: when a test errors, run the module under pdb and let it drop
  you at the crash site with every local intact:
  ```bash
  python3 -m pdb -c continue test_inventory_audit.py
  ```
- **Conditional breakpoints**: `b inventory_audit.py:38, row["sku"] == "COF-1"` stops only when the condition holds — invaluable in loops.

## Suggested session (the skill being practiced)

1. Pick ONE failing test. Read its assertion: what value is wrong?
2. Put `breakpoint()` at the top of the function under test. Run just that test.
3. `pp` the inputs. Are they what the test passed in? (If not, something earlier corrupted them.)
4. `n` through the function, `pp`-ing the suspect structure after each line. The first line after which the data is wrong *is* the bug — read that line character by character.
5. When you suspect an unintended side effect, inspect the caller's value
   before and after the call, then step into the call to find the first write.

There are 3 bugs. If you get stuck, use [HINTS.md](HINTS.md).

## After you finish

- `PYTHONBREAKPOINT=0 python3 -m unittest` turns any forgotten `breakpoint()` into a no-op — set it in CI so a leftover breakpoint can't hang a build.
- In an interview, narrating "I'll break here and inspect the rows before and after the call" demonstrates exactly the systematic isolate-step from Guide 04 — with a tool that's faster than prints once the data is nested.
