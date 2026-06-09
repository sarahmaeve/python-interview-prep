# Solution: Exercise 35 — Debugging with pdb

## Bugs Found

1. **`parse_rows` drops the last data line.** `raw_lines[1:-1]` was meant to skip the header but trims one line off BOTH ends.

2. **`merge_duplicates` corrupts its input through an alias.** `merged[sku] = row` stores a reference to the caller's dict; the later `merged[sku]["qty"] += row["qty"]` writes through that reference, so the caller's "unchanged" rows silently change. A second symptom: calling the function twice on the same input gives different answers, because the input mutated in between.

3. **`apply_adjustments` writes at the wrong indentation.** `row["qty"] = new_qty` sits *outside* the inner loop, so the adjustment lands on whichever row the loop finished on — and when no row matched at all, `new_qty` was never bound and the line raises `NameError`.

## The pdb sessions that find them

**Bug 1** — break at the top of `parse_rows`, run only the failing test:

```
(Pdb) pp raw_lines
['sku,qty', 'COF-1,10', 'TEA-2,4', 'MUG-3,7']
(Pdb) c            # let it finish, or `n` to the return and:
(Pdb) pp rows
[{'qty': 10, 'sku': 'COF-1'}, {'qty': 4, 'sku': 'TEA-2'}]
```

Four input lines, one header — but two rows. Re-read the `for` line: `[1:-1]`.

**Bug 2** — the corruption shows in the *caller*, so inspect around the call:

```
(Pdb) pp rows
[{'qty': 10, 'sku': 'COF-1'}, {'qty': 5, 'sku': 'COF-1'}]
(Pdb) n            # step over merge_duplicates(rows)
(Pdb) pp rows
[{'qty': 15, 'sku': 'COF-1'}, {'qty': 5, 'sku': 'COF-1'}]
```

The function changed data it promised not to touch. `s` into it and watch: `merged[sku] = row` stores the caller's dict — `p merged['COF-1'] is rows[0]` prints `True`, and the `is` check is the definitive aliasing test.

**Bug 3** — the ERROR is fastest via post-mortem (`python3 -m pdb -c continue test_inventory_audit.py` drops you at the `NameError` with locals intact: `p target_sku` shows `'GHOST-0'`, and `new_qty` doesn't exist). For the FAIL, step the inner loop and note that `row["qty"] = new_qty` only executes once — after the loop, on the final `row`.

## The Fixes

```python
# parse_rows
for line in raw_lines[1:]:

# merge_duplicates
merged[sku] = dict(row)        # copy, never alias the caller's data

# apply_adjustments
for row in rows:
    if row["sku"] == target_sku:
        row["qty"] = row["qty"] + delta
# (delete the dangling `row["qty"] = new_qty` line entirely)
```

## Why This Matters

- **Aliasing bugs are invisible to prints at the wrong altitude.** Printing the *result* of `merge_duplicates` shows correct totals; only inspecting the *input* after the call reveals the damage. The debugger makes before/after inspection cheap, and `a is b` answers "same object?" definitively.
- **Indentation bugs read correctly.** Your eye parses the intent ("assign inside the if"), not the actual structure. Watching execution with `n` shows the truth: the assignment runs once, after the loop.
- **Post-mortem debugging beats re-reading for crashes.** `python3 -m pdb -c continue ...` (or `import pdb; pdb.pm()` in a REPL after an exception) parks you at the crash frame with every local alive — the `NameError` here explains itself in two `p` commands.
- The interview version of this skill is narration: "the data is right here, wrong there, so the bug is between — let me step that region." That's Guide 04's binary-search isolation executed with a real tool.

## Discussion

- `new_qty`'s `NameError` only fired for an unmatched SKU; with a match earlier in the list, the bug *silently* corrupted a different row instead. Errors are gifts — the silent variant of the same bug shipped.
- The defensive-copy fix (`dict(row)`) matches Guide 02 §8's rule, applied on the way IN: never store references to data the caller still owns (and might rely on).
- `pdb` ships everywhere; richer frontends (`ipdb`, IDE debuggers) share the same command vocabulary, so fluency transfers. `PYTHONBREAKPOINT` picks the implementation without code changes.
