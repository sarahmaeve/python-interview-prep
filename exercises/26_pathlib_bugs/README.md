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

## Principle Primer

Paths have structure: a filename, parent directory, and one or more suffixes.
`stem` removes only the final suffix, while `suffixes` exposes a compound
extension. When mirroring a tree, join the destination with the source's
relative parent, not the filename as though it were a directory. Choose
recursive discovery deliberately when nested files are part of the contract.

If you get stuck, use [HINTS.md](HINTS.md).

## Relevant reading

- `guides/10_paths_and_matching.py` — Sections 1–4 (pathlib basics, suffixes, rglob, tempfile)
