"""
Guide 10 — Paths and Pattern Matching
======================================
Run:  python guides/10_paths_and_matching.py

Two idioms that modern (3.10+) Python gives us, and that you should reach
for any time you'd otherwise write:
  - string-concatenated paths or os.path.join
  - long if/elif chains dispatching on structure or type

    pathlib.Path   — object-oriented filesystem paths (stdlib since 3.4
                     but still underused vs str paths in tutorials)
    match / case   — structural pattern matching (PEP 634, 3.10+)

Both make code that's harder to get wrong.  pathlib normalises separators
and edge cases you'd have to remember; match + typing.assert_never give
you exhaustiveness that mypy can verify.

TABLE OF CONTENTS
  1. pathlib basics and the why of it       (line ~35)
  2. Joining, parts, suffixes                (line ~110)
  3. Reading and writing via Path            (line ~170)
  4. pathlib + tempfile in tests             (line ~220)
  5. match / case: literal patterns          (line ~270)
  6. match / case: sequence and mapping      (line ~320)
  7. match / case: class patterns and guards (line ~380)
  8. Exhaustiveness with assert_never        (line ~450)
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import assert_never


# ============================================================================
# 1. pathlib BASICS AND THE WHY OF IT
# ============================================================================
#
# String paths mostly work.  They also lie to you:
#
#     >>> "/etc/" + "/hosts"
#     "/etc//hosts"              # double slash; some tools handle it, some don't
#     >>> os.path.join("/etc", "/hosts")
#     "/hosts"                   # wait, what?
#     >>> "path/to/file.tar.gz".replace(".tar.gz", "")
#     "path/to/file"             # oops, no — that also removed ".tar.gz" from
#                                  mid-path components if any existed
#
# Path(...) is the fix.  It:
#   - normalises separators
#   - gives you named accessors for parts, stem, suffix, name, parent
#   - implements operator `/` for joining
#   - has methods for I/O (read_text, write_text, iterdir, etc.)


def demo_pathlib_basics() -> None:
    print("=" * 60)
    print("1. pathlib basics")
    print("=" * 60)

    # Path joins via `/` — reads left-to-right, handles separators for you.
    base = Path("/var/log")
    p = base / "myapp" / "errors.log"
    assert str(p) == "/var/log/myapp/errors.log"
    print(f"  Path('/var/log') / 'myapp' / 'errors.log' = {p}")

    # An absolute second argument does the os.path.join trap.
    # Path handles it predictably by starting fresh from the absolute part.
    weird = Path("/etc") / "/hosts"
    print(f"  Path('/etc') / '/hosts'                    = {weird}")
    print("  (absolute RHS resets — but at least it's documented, not surprising)")

    # Parts, parent, name, stem, suffix — named, unambiguous.
    p2 = Path("/home/sarah/data/report.tar.gz")
    print(f"  Path: {p2}")
    print(f"    parts    = {p2.parts}")
    print(f"    parent   = {p2.parent}")
    print(f"    name     = {p2.name}")
    print(f"    stem     = {p2.stem}       (just 'report.tar' — .suffix is last only)")
    print(f"    suffix   = {p2.suffix}")
    print(f"    suffixes = {p2.suffixes}   (all suffixes as a list)")

    # Path.with_* methods create a new path with one part changed.
    print(f"  p2.with_suffix('.zip') = {p2.with_suffix('.zip')}")
    print(f"  p2.with_name('summary.md') = {p2.with_name('summary.md')}")
    print(f"  p2.with_stem('backup')     = {p2.with_stem('backup')}")
    print()


# ============================================================================
# 2. JOINING, PARTS, SUFFIXES
# ============================================================================
#
# A repeating pitfall in string-based path code: handling double-suffix files
# like `archive.tar.gz`.  Naive string replace removes .tar.gz from ANY
# position in the path, not just the end.  pathlib.Path.suffixes gives you
# the list; `with_suffix('')` strips ONE suffix at a time.


def demo_paths_pitfalls() -> None:
    print("=" * 60)
    print("2. Joining, parts, suffixes — common pitfalls")
    print("=" * 60)

    # Pitfall: string replace on a path.
    p = "data.tar.gz/backup.tar.gz"
    naive = p.replace(".tar.gz", "")
    # Expected "data.tar.gz/backup" but got "data/backup" — both suffixes stripped.
    print(f"  str.replace('.tar.gz', '') on {p!r}")
    print(f"    naive:         {naive!r}   <- removed BOTH occurrences!")

    # With Path, stripping ONLY the trailing suffix is unambiguous:
    only_base = Path("backup.tar.gz").with_suffix("")
    assert str(only_base) == "backup.tar"
    print(f"  Path('backup.tar.gz').with_suffix('')  = {only_base}")

    # To strip ALL suffixes:
    full_stem = Path("backup.tar.gz")
    while full_stem.suffix:
        full_stem = full_stem.with_suffix("")
    print(f"  strip all suffixes: -> {full_stem}")

    # Joining with `/` handles separators consistently.
    joined = Path("a") / "b/c" / "d"
    print(f"  Path('a') / 'b/c' / 'd' = {joined}   (mixed separators normalised)")
    print()


# ============================================================================
# 3. READING AND WRITING VIA Path
# ============================================================================
#
# Path has built-in I/O methods.  They're convenient for whole-file ops;
# for streaming, open() via `with path.open():` is idiomatic.


def demo_pathlib_io() -> None:
    print("=" * 60)
    print("3. Reading and writing via Path")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # write_text / read_text — simplest possible file I/O.
        hello = root / "hello.txt"
        hello.write_text("hi there\n", encoding="utf-8")
        assert hello.read_text(encoding="utf-8") == "hi there\n"
        print(f"  {hello.name}.read_text() round-trips OK")

        # write_bytes / read_bytes for binary.
        data = root / "blob.bin"
        data.write_bytes(b"\x00\x01\x02")
        assert data.read_bytes() == b"\x00\x01\x02"

        # mkdir with parents=True, exist_ok=True — the "make it so" combo.
        nested = root / "a" / "b" / "c"
        nested.mkdir(parents=True, exist_ok=True)
        assert nested.is_dir()
        print(f"  created nested {nested.relative_to(root)}")

        # Streaming via path.open() — context manager handles the close.
        streaming = root / "stream.txt"
        with streaming.open("w", encoding="utf-8") as f:
            for i in range(3):
                f.write(f"line {i}\n")

        # Iteration: iterdir for direct children, rglob for recursive.
        children = sorted(root.iterdir())
        print(f"  root has {len(children)} top-level entries")
        txts = sorted(root.rglob("*.txt"))
        print(f"  rglob('*.txt') found {len(txts)} text files")
    print()


# ============================================================================
# 4. pathlib + tempfile IN TESTS
# ============================================================================
#
# The pytest `tmp_path` fixture gives you a Path pointing at a per-test
# temp directory.  In plain unittest, tempfile.TemporaryDirectory() is
# the direct equivalent.  Either way: DON'T write to the CWD, DON'T
# hard-code /tmp, DON'T rely on teardown to clean up.


def demo_tempfile_with_pathlib() -> None:
    print("=" * 60)
    print("4. pathlib + tempfile in tests")
    print("=" * 60)

    # Pattern A: context manager (cleans up at end of block).
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        log = root / "app.log"
        log.write_text("start\n")
        log.write_text("start\nprocessing\n")
        assert "processing" in log.read_text()
        print(f"  wrote and read {log}")

    # After the `with` block, the directory no longer exists.
    assert not root.exists()

    # Pattern B: pytest's tmp_path fixture (equivalent, no boilerplate).
    # In a pytest test:
    #     def test_writes_log(tmp_path: Path):
    #         log = tmp_path / "app.log"
    #         ...
    print("  pytest equivalent:  def test_x(tmp_path: Path): ...")
    print()


# ============================================================================
# 5. match / case: LITERAL PATTERNS
# ============================================================================
#
# match/case replaces deep if/elif chains where you're dispatching on the
# SHAPE of a value.  The simplest use is literal patterns, which is
# Python's closest equivalent to C's switch.


def demo_match_literals() -> None:
    print("=" * 60)
    print("5. match / case: literal patterns")
    print("=" * 60)

    def http_status_label(code: int) -> str:
        match code:
            case 200:
                return "OK"
            case 301 | 302:               # alternation with |
                return "redirect"
            case 404:
                return "not found"
            case code if 500 <= code < 600:  # guard clause
                return "server error"
            case _:                       # wildcard — like `default:`
                return "other"

    for c in (200, 301, 302, 404, 503, 418):
        print(f"  {c} -> {http_status_label(c)}")
    print()


# ============================================================================
# 6. match / case: SEQUENCE AND MAPPING PATTERNS
# ============================================================================
#
# match can destructure sequences and dicts directly.  Use this when you're
# parsing a small piece of structured data (a command, a JSON message, an
# event) instead of a chain of len()/isinstance()/indexing checks.


def demo_match_structural() -> None:
    print("=" * 60)
    print("6. match / case: sequence and mapping")
    print("=" * 60)

    def describe_command(cmd: list[str]) -> str:
        match cmd:
            case []:
                return "empty command"
            case [single]:
                return f"one arg: {single}"
            case ["help", *rest]:                 # rest captures remaining items
                return f"help topic: {rest}"
            case ["move", x, y]:                  # exact-length with captures
                return f"move to ({x}, {y})"
            case [head, *tail]:
                return f"{head} with tail {tail}"

    for cmd in [[], ["version"], ["help", "config", "syntax"], ["move", "3", "4"],
                ["noop", "arg1", "arg2"]]:
        print(f"  {cmd!r:40s} -> {describe_command(cmd)}")

    # Mapping patterns: match dict *subsets*.  Keys not mentioned are ignored.
    def classify_event(event: dict) -> str:
        match event:
            case {"type": "click", "x": x, "y": y}:
                return f"click at ({x}, {y})"
            case {"type": "scroll", "delta": d}:
                return f"scroll {d}"
            case {"type": t}:
                return f"unknown event type: {t}"
            case _:
                return "malformed event"

    events = [
        {"type": "click", "x": 10, "y": 20, "button": "left"},
        {"type": "scroll", "delta": -5},
        {"type": "resize"},
        {"noise": True},
    ]
    for e in events:
        print(f"  {e!r:55s} -> {classify_event(e)}")
    print()


# ============================================================================
# 7. match / case: CLASS PATTERNS AND GUARDS
# ============================================================================
#
# Class patterns let you destructure dataclasses and other classes by
# position or by keyword.  Combined with guards (the `if` after a pattern),
# they replace messy isinstance+attribute-access chains.


@dataclass
class Point2D:
    x: float
    y: float


@dataclass
class Point3D:
    x: float
    y: float
    z: float


def demo_match_classes() -> None:
    print("=" * 60)
    print("7. match / case: class patterns and guards")
    print("=" * 60)

    def describe(p: Point2D | Point3D) -> str:
        match p:
            case Point2D(0, 0):
                return "2D origin"
            case Point3D(0, 0, 0):
                return "3D origin"
            case Point2D(x, y) if x == y:
                return f"2D diagonal at {x}"
            case Point2D(x, y):
                return f"2D point ({x}, {y})"
            case Point3D(x=x, y=y, z=z):         # keyword destructuring
                return f"3D point ({x}, {y}, {z})"

    for p in [Point2D(0, 0), Point3D(0, 0, 0), Point2D(5, 5), Point2D(1, 2),
              Point3D(1, 2, 3)]:
        print(f"  {p!s:40s} -> {describe(p)}")
    print()


# ============================================================================
# 8. EXHAUSTIVENESS WITH typing.assert_never
# ============================================================================
#
# match/case does NOT check exhaustiveness at runtime by itself.  If you
# forget a case, execution falls through and returns None — a silent bug.
#
# The fix is typing.assert_never (3.11+).  Put it in an `else` branch (or
# `case _` that reaches it).  mypy will verify that every case is handled;
# at runtime it raises AssertionError if you get there anyway.
#
# Use this pattern ANY time the value is typed as a finite union or Enum.


@dataclass
class Quit:  pass


@dataclass
class Move:
    dx: int
    dy: int


@dataclass
class Say:
    message: str


Command = Quit | Move | Say


def handle_command(cmd: Command) -> str:
    """Exhaustiveness-checked dispatch on a closed union."""
    match cmd:
        case Quit():
            return "goodbye"
        case Move(dx, dy):
            return f"moved by ({dx}, {dy})"
        case Say(message):
            return f"said: {message!r}"
        case _ as unhandled:
            # If you add a new Command variant and forget to handle it here,
            # mypy will flag this assert_never call.
            assert_never(unhandled)


def demo_exhaustiveness() -> None:
    print("=" * 60)
    print("8. Exhaustiveness with typing.assert_never")
    print("=" * 60)

    for c in [Quit(), Move(3, 4), Say("hello")]:
        print(f"  {c!s:30s} -> {handle_command(c)}")

    print("""
  Why this matters: without assert_never(), match statements silently
  fall through to None when you add a new variant and forget to handle
  it.  With assert_never(), mypy catches the miss BEFORE you run the code.
  Exercise 27 walks through a real bug caused by a missed match case.
""")


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    demo_pathlib_basics()
    demo_paths_pitfalls()
    demo_pathlib_io()
    demo_tempfile_with_pathlib()
    demo_match_literals()
    demo_match_structural()
    demo_match_classes()
    demo_exhaustiveness()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Prefer pathlib.Path over string paths.  `/` for joining,")
    print("     .parts/.stem/.suffix for decomposition, .read_text/.write_text")
    print("     for whole-file I/O.")
    print("  2. In tests, tempfile.TemporaryDirectory() (or pytest's tmp_path)")
    print("     is the idiomatic place to write files.")
    print("  3. match/case replaces if/elif chains that dispatch on shape.")
    print("     Literal, sequence, mapping, and class patterns all compose.")
    print("  4. Pair match/case with assert_never (3.11+) so mypy can verify")
    print("     you've handled every variant of a closed union or Enum.")
    print()
    print("  Next up:")
    print("    Exercise 26 — pathlib Bugs          (path manipulation bugs)")
    print("    Exercise 27 — match/case Dispatch   (missed-case silent return)")
    print()


if __name__ == "__main__":
    main()
