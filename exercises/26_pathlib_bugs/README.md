# Exercise 26: pathlib Bugs

A backup tool that mirrors a source tree into a timestamped backup directory. The implementation has **3 bugs** in how it handles paths.

## How to run the tests

```bash
cd exercises/26_pathlib_bugs
python3 -m unittest test_backup_tool
```

Your goal is to edit `backup_tool.py` until all tests pass. Do **not** modify the test file.

## What the tool does

```
source/docs/notes.txt      ─▶  backup/docs/notes.<timestamp>.bak.txt
source/archive.tar.gz      ─▶  backup/archive.<timestamp>.bak.tar.gz
source/.hidden/file.txt    (skipped)
```

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

Each bug is in a different function. Run the tests and note which function the failures point at.

The trickiest of the three has to do with `.tar.gz` — the double-suffix case. `Path.stem` only strips ONE suffix at a time.

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `build_backup_name` uses `source_file.stem`, which only strips the last suffix. For compound suffixes like `.tar.gz`, the remaining `.tar` leaks into the base.
2. `backup_path` composes the destination as `backup_root / relative_file / dest_name`, treating the source filename as a directory.
3. `iter_source_files` uses `glob("*")` — non-recursive. Nested files aren't discovered.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. In `build_backup_name`, strip the full suffix string from the name:
    ```python
    base = source_file.name.removesuffix(suffixes)
    ```
2. In `backup_path`, use `relative_file.parent` rather than `relative_file`:
    ```python
    return backup_root / relative_file.parent / dest_name
    ```
3. In `iter_source_files`, recurse:
    ```python
    for entry in source.rglob("*"):
    ```

</details>

## Relevant reading

- `guides/10_paths_and_matching.py` — Sections 1–4 (pathlib basics, suffixes, rglob, tempfile)
