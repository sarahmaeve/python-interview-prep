# Exercise 35: Debugging with pdb

An inventory audit pipeline (`inventory_audit.py`) has **3 bugs**. They're deliberately the kind that are easy to gloss over when reading — data corrupted by an alias two frames away, a write that happens one indentation level too far out, a slice that quietly eats a row. The point of this exercise is the *method*: find them with the debugger, not with `print()`.

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
python3 -m unittest test_inventory_audit.TestMergeDuplicates.test_input_rows_are_not_modified
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

- **Post-mortem**: when a test ERRORs (like the `NameError` in this suite), run the module under pdb and let it drop you at the crash site with every local intact:
  ```bash
  python3 -m pdb -c continue test_inventory_audit.py
  ```
- **Conditional breakpoints**: `b inventory_audit.py:38, row["sku"] == "COF-1"` stops only when the condition holds — invaluable in loops.

## Suggested session (the skill being practiced)

1. Pick ONE failing test. Read its assertion: what value is wrong?
2. Put `breakpoint()` at the top of the function under test. Run just that test.
3. `pp` the inputs. Are they what the test passed in? (If not, something earlier corrupted them.)
4. `n` through the function, `pp`-ing the suspect structure after each line. The first line after which the data is wrong *is* the bug — read that line character by character.
5. For the corruption bug: `pp rows` *before* and *after* the call that isn't supposed to modify them. When you see them change, `s` INTO the call and watch which line writes through the alias.

## Bugs: 3

<details>
<summary>Hint 1 (gentle — method, not location)</summary>

Chase the three failures separately: one function returns too little data, one modifies something it promised not to, one writes to the wrong place. For each, the session above will corner the line in under ten steps. For the ERROR, use post-mortem pdb and `p` the loop variables at the crash.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. In `parse_rows`, `pp rows` just before the return and count them against the input lines. Look hard at the slice in the `for` statement.
2. In the merge test, `pp rows` after `merge_duplicates(rows)` returns — the caller's dicts changed. Step into the function and watch which assignment stores a *reference* instead of a copy.
3. In `apply_adjustments`, step the inner loop with `n` and `p row` at each iteration — then notice which iteration the `row["qty"] = ...` line actually runs on, and at which indentation level it sits.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **`parse_rows`**: `raw_lines[1:-1]` skips the header AND the last line. Use `raw_lines[1:]`.
2. **`merge_duplicates`**: `merged[sku] = row` stores the caller's dict; the later `merged[sku]["qty"] +=` then mutates the caller's data. Store a copy: `merged[sku] = dict(row)`.
3. **`apply_adjustments`**: `row["qty"] = new_qty` sits OUTSIDE the inner loop, so it writes the adjustment onto whatever row the loop ended on (and raises NameError when nothing matched). Move the assignment inside the `if`: `row["qty"] = row["qty"] + delta`, and delete the dangling line.

</details>

## After you finish

- `PYTHONBREAKPOINT=0 python3 -m unittest` turns any forgotten `breakpoint()` into a no-op — set it in CI so a leftover breakpoint can't hang a build.
- In an interview, narrating "I'll break here and inspect the rows before and after the call" demonstrates exactly the systematic isolate-step from Guide 04 — with a tool that's faster than prints once the data is nested.
