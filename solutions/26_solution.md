# Solution: Exercise 26 — pathlib Bugs

## Bugs Found

1. **`build_backup_name` uses `Path.stem` for the base name.** `Path.stem` strips ONE suffix at a time. For compound suffixes like `.tar.gz`, `Path("archive.tar.gz").stem` is `"archive.tar"`, so the built name is `"archive.tar.<when>.bak.tar.gz"` — the `.tar` leaks into the middle.

2. **`backup_path` joins `relative_file` itself as a directory segment.** `backup_root / relative_file / dest_name` treats the source file's name as a folder — the destination ends up one level too deep, under a directory named after the source file.

3. **`iter_source_files` uses `source.glob("*")` instead of `source.rglob("*")`.** `glob` is not recursive; any file nested below the top level is silently missed.

## Diagnosis Process

- `test_compound_suffix_tar_gz` fails because the result has `.tar` in the stem position. Inspecting `build_backup_name`, the offending line is `base = source_file.stem` — check what `.stem` produces for multi-suffix filenames.
- `test_nested_file` fails with a path that has the source name embedded as a directory. Walking the expression by hand reveals the culprit.
- `test_discovers_nested_files` fails because nested files aren't in the result. The fix is swapping `glob` for `rglob`.

## The Fix

### Bug 1 — strip the FULL suffix

```python
def build_backup_name(source_file: Path, when: str) -> Path:
    suffixes = "".join(source_file.suffixes)
    base = source_file.name.removesuffix(suffixes)   # FIX
    name = f"{base}.{when}.bak{suffixes}"
    return Path(name)
```

`str.removesuffix` (3.9+) strips an exact suffix if present, or returns the string unchanged. Perfect for this case.

### Bug 2 — use `relative_file.parent`

```python
def backup_path(backup_root: Path, relative_file: Path, when: str) -> Path:
    dest_name = build_backup_name(relative_file, when)
    return backup_root / relative_file.parent / dest_name
```

### Bug 3 — recursive glob

```python
def iter_source_files(source: Path) -> list[Path]:
    results: list[Path] = []
    for entry in source.rglob("*"):   # FIX
        if not entry.is_file():
            continue
        rel = entry.relative_to(source)
        if any(part.startswith(".") for part in rel.parts):
            continue
        results.append(rel)
    return sorted(results)
```

## Why This Bug Matters

- **`Path.stem` ≠ "base name with all suffixes stripped".** The docs are explicit that it strips one suffix. For compound suffixes (`.tar.gz`, `.tar.bz2`, `log.out.gz`), reach for `.suffixes` (a list) and `removesuffix`.
- **Paths compose via `/`, not string concatenation.** `Path` respects parts: it knows what "parent" means, what "name" means, what "suffixes" mean. Using the typed accessors prevents a class of bugs that raw string manipulation silently allows.
- **`glob` vs. `rglob`.** This is the default gotcha — new pathlib users often expect `glob("*")` to recurse because `**` is available. It doesn't; you need `rglob` (or `glob("**/*")`).
- **Hidden-directory filtering.** Checking only the filename is the common bug. If you care about anywhere in the path starting with `.`, iterate through `rel.parts` or use `any(part.startswith(".") for part in rel.parts)`.

## Discussion

- The test `test_skips_files_inside_hidden_directories` uses `.secrets/key.pem`. Real-world analogues include `.git`, `.venv`, `__pycache__`. A tool that backs up `__pycache__` contents wastes space and could leak build-time state to ops folks reading backups.
- For the `.tar.gz` case specifically, consider not using the name-manipulation approach at all — use `source_file.parent / f"{...}"` and build the full path deliberately.
- `tempfile.TemporaryDirectory()` (and pytest's `tmp_path`) are the idiomatic way to test filesystem code. They auto-cleanup; you never leave garbage behind.
- Hidden-file detection across platforms is subtle (Windows has "hidden" attributes; macOS has `.DS_Store` conventions). The `startswith(".")` convention is POSIX-idiomatic; if your code runs on Windows, consider using `pathlib.Path.stat().st_file_attributes`.
