"""Backup tool — contains 3 bugs around path handling.

A small module that scans a source directory and copies every file into
a parallel directory under a backup root, preserving the relative tree.
Files are renamed so successive backups don't overwrite each other:

    <stem>.<timestamp>.bak<suffix>

Example:
    source/docs/notes.txt   ->   backup/docs/notes.20260416T120000.bak.txt
    source/archive.tar.gz   ->   backup/archive.20260416T120000.bak.tar.gz

The code mixes pathlib.Path and raw string manipulation — and each of
the three bugs falls at one of those seams.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading: guides/10_paths_and_matching.py Sections 1–4.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path


def timestamp_now() -> str:
    """ISO-like timestamp safe for filenames (no colons)."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def build_backup_name(source_file: Path, when: str) -> Path:
    """Return the backup FILENAME for *source_file*.

    The stem keeps its name, a dotted timestamp is inserted, and the
    suffix is preserved.  Double suffixes like `.tar.gz` are kept whole
    — they are NOT split at every dot.

    Examples:
        notes.txt        -> notes.<when>.bak.txt
        archive.tar.gz   -> archive.<when>.bak.tar.gz
        dotfile          -> dotfile.<when>.bak
    """
    suffixes = "".join(source_file.suffixes)
    base = source_file.stem
    name = f"{base}.{when}.bak{suffixes}"
    return Path(name)


def backup_path(backup_root: Path, relative_file: Path, when: str) -> Path:
    """Compute the full backup destination for *relative_file*.

    *relative_file* is the source file's path relative to the source
    root.  The destination mirrors that relative tree under *backup_root*.
    """
    dest_name = build_backup_name(relative_file, when)
    return backup_root / relative_file / dest_name


def iter_source_files(source: Path) -> list[Path]:
    """Return every regular file under *source*, as paths RELATIVE to source.

    Hidden files and files inside hidden directories (any path part that
    begins with '.') are skipped.
    """
    results: list[Path] = []
    for entry in source.glob("*"):
        if not entry.is_file():
            continue
        rel = entry.relative_to(source)
        if any(part.startswith(".") for part in rel.parts):
            continue
        results.append(rel)
    return sorted(results)


def run_backup(source: Path, backup_root: Path, when: str | None = None) -> list[Path]:
    """Copy every eligible file from *source* into *backup_root*.

    Returns the list of DESTINATION paths that were written.  The
    destination directory tree is created as needed.
    """
    when = when or timestamp_now()
    written: list[Path] = []

    for relative_file in iter_source_files(source):
        src_file = source / relative_file
        dest_file = backup_path(backup_root, relative_file, when)

        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        written.append(dest_file)

    return written
