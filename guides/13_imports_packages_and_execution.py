"""
Guide 13 — Imports, Packages, and Module Execution
===================================================
Run:  python guides/13_imports_packages_and_execution.py

Imports are executable behavior, not textual file inclusion.  This guide uses
temporary packages and fresh Python processes so that working-directory state
and the import cache cannot hide what is happening.

TABLE OF CONTENTS
  1. Module identity and the import cache
  2. sys.path and package context
  3. Relative imports and python -m
  4. __main__.py and entry points
  5. Circular imports and type-only dependencies
  6. Testing import behavior in fresh processes

OFFICIAL DOCUMENTATION
  Modules and packages tutorial:
    https://docs.python.org/3/tutorial/modules.html
  The import system:
    https://docs.python.org/3/reference/import.html
  __main__ and package entry points:
    https://docs.python.org/3/library/__main__.html
  importlib:
    https://docs.python.org/3/library/importlib.html
  typing.TYPE_CHECKING:
    https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import tempfile
from pathlib import Path

# ============================================================================
# 1. MODULE IDENTITY AND THE IMPORT CACHE
# ============================================================================
#
# On first import, Python creates a module object, places it in sys.modules,
# and executes the module's top-level code.  Later imports normally reuse that
# same object.  Import-time side effects therefore happen once per interpreter,
# not once per import statement.


def demo_import_cache() -> None:
    print("=" * 60)
    print("1. Module identity and the import cache")
    print("=" * 60)

    first = importlib.import_module("email")
    second = importlib.import_module("email")

    assert first is second
    assert sys.modules["email"] is first
    print(f"  repeated imports return one module object: {first is second}")
    print(f"  sys.modules holds that object:            {sys.modules['email'] is first}")
    print("  Consequence: keep library-module top-level work cheap and quiet.")
    print()


# ============================================================================
# 2. sys.path AND PACKAGE CONTEXT
# ============================================================================
#
# sys.path contains directories Python searches for TOP-LEVEL names.  To
# import `parcel_demo`, its parent directory must be searchable; the package
# directory itself is not the top-level search root.
#
# Once a module is found inside a package, __package__ records its package
# context.  Relative imports resolve from that context rather than from the
# current working directory.


def create_demo_package(root: Path) -> Path:
    package = root / "parcel_demo"
    package.mkdir()

    (package / "__init__.py").write_text(
        '"""Small package created by Guide 13."""\n'
        "from .labels import describe\n",
        encoding="utf-8",
    )
    (package / "labels.py").write_text(
        "def describe(name: str) -> str:\n"
        "    return f'label:{name}'\n",
        encoding="utf-8",
    )
    (package / "__main__.py").write_text(
        "from .labels import describe\n"
        "print(f'__name__={__name__}')\n"
        "print(f'__package__={__package__}')\n"
        "print(describe('parcel'))\n",
        encoding="utf-8",
    )
    (package / "models.py").write_text(
        "from dataclasses import dataclass\n\n"
        "@dataclass(frozen=True)\n"
        "class Parcel:\n"
        "    code: str\n",
        encoding="utf-8",
    )
    (package / "service.py").write_text(
        "from typing import TYPE_CHECKING\n\n"
        "if TYPE_CHECKING:\n"
        "    from .models import Parcel\n\n"
        "def summary(parcel: 'Parcel') -> str:\n"
        "    return f'parcel:{parcel.code}'\n",
        encoding="utf-8",
    )
    return package


def run_python(
    cwd: Path, *arguments: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def demo_search_path_and_context(root: Path) -> None:
    print("=" * 60)
    print("2. sys.path and package context")
    print("=" * 60)

    code = (
        "import parcel_demo.labels as labels; "
        "print(labels.__package__); "
        "print(labels.describe('box'))"
    )
    result = run_python(root, "-c", code)
    package_name, description = result.stdout.strip().splitlines()

    assert package_name == "parcel_demo"
    assert description == "label:box"
    print(f"  package context: {package_name}")
    print(f"  relative import result: {description}")
    print("  Search root is the directory containing parcel_demo.")
    print()


# ============================================================================
# 3. RELATIVE IMPORTS AND python -m
# ============================================================================
#
# `python path/to/file.py` executes a file and initially calls it __main__.
# It does not infer the package relationship merely from surrounding folders.
# `python -m package` resolves through the import system first, then executes
# package/__main__.py with package context intact.


def demo_module_execution(root: Path, package: Path) -> None:
    print("=" * 60)
    print("3. Relative imports and python -m")
    print("=" * 60)

    module_result = run_python(root, "-m", "parcel_demo")
    output = module_result.stdout.strip().splitlines()
    assert output == ["__name__=__main__", "__package__=parcel_demo", "label:parcel"]

    direct_result = run_python(root, str(package / "__main__.py"), check=False)
    assert direct_result.returncode != 0
    assert "attempted relative import" in direct_result.stderr

    print("  python -m parcel_demo:")
    for line in output:
        print(f"    {line}")
    print("  direct __main__.py execution lacks package context and fails.")
    print("  Do not repair that difference by editing sys.path in application code.")
    print()


# ============================================================================
# 4. __main__.py AND ENTRY POINTS
# ============================================================================
#
# A package's __main__.py is the code used by `python -m package`.  Keep it
# thin: parse command-line arguments, call an importable function, and choose
# an exit status.  Business logic then remains directly testable.


def explain_entry_points() -> None:
    print("=" * 60)
    print("4. __main__.py and entry points")
    print("=" * 60)
    print("  Prefer a thin entry point:")
    print("    from .cli import main")
    print("    raise SystemExit(main())")
    print("  Importing the package should not unexpectedly print, parse argv,")
    print("  connect to services, or start an application loop.")
    print()


# ============================================================================
# 5. CIRCULAR IMPORTS AND TYPE-ONLY DEPENDENCIES
# ============================================================================
#
# A module is present in sys.modules while its body is still executing.  If A
# imports B and B immediately reads a name that A has not defined yet, B sees a
# partially initialized module.  Moving imports around can hide the symptom
# without repairing the dependency cycle.
#
# If a dependency exists only for static annotations, TYPE_CHECKING keeps it
# visible to type checkers without importing it at runtime.  If both modules
# genuinely need each other's runtime objects, extract the shared contract or
# data type into a third module instead.


def demo_type_only_dependency(root: Path) -> None:
    print("=" * 60)
    print("5. Circular imports and type-only dependencies")
    print("=" * 60)

    code = (
        "from parcel_demo.models import Parcel; "
        "from parcel_demo.service import summary; "
        "print(summary(Parcel('PX-7')))"
    )
    result = run_python(root, "-c", code)
    assert result.stdout.strip() == "parcel:PX-7"
    print(f"  type-only dependency result: {result.stdout.strip()}")
    print("  TYPE_CHECKING is False at runtime but understood by type checkers.")
    print("  Prefer a third shared module when the dependency is needed at runtime.")
    print()


# ============================================================================
# 6. TESTING IMPORT BEHAVIOR IN FRESH PROCESSES
# ============================================================================


def explain_import_tests() -> None:
    print("=" * 60)
    print("6. Testing import behavior in fresh processes")
    print("=" * 60)
    print("  A fresh subprocess can vary:")
    print("    - working directory and search path")
    print("    - import order")
    print("    - `import package` versus `python -m package`")
    print("    - captured stdout and stderr")
    print("  In-process tests can accidentally pass because sys.modules remembers")
    print("  an earlier import. importlib.reload is not a complete fresh-process model.")
    print()


def main() -> None:
    demo_import_cache()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package = create_demo_package(root)
        demo_search_path_and_context(root)
        demo_module_execution(root, package)
        explain_entry_points()
        demo_type_only_dependency(root)
    explain_import_tests()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Imports execute module top-level code once and cache the module.")
    print("  2. sys.path searches for top-level names; package context resolves dots.")
    print("  3. Use python -m for package entry points; keep __main__.py thin.")
    print("  4. Remove unnecessary runtime dependencies instead of patching sys.path.")
    print("  5. Test import behavior in fresh processes when interpreter state matters.")


if __name__ == "__main__":
    main()
