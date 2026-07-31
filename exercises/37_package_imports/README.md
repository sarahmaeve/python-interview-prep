# Exercise 37: Package Imports

The small `inventory_tool` package has **3 import-related bugs**. Depending on
how it is loaded, it either prints unexpectedly, cannot start, or fails while
two modules are still being initialized.

**This exercise practices:** reading package structure, reasoning about
`sys.path` and package context, using `python -m`, and untangling circular
imports caused by type annotations.

## How to run the tests

```bash
cd exercises/37_package_imports
python3 -m unittest test_package_imports -v
```

The tests launch fresh Python subprocesses from temporary working directories.
That isolation is deliberate: imports cached in `sys.modules` must not make a
later test pass accidentally, and the package must not depend on the shell
being in this exercise directory.

## Ground rules

- Modify files under `inventory_tool/`; do not modify the tests.
- Do not add the exercise directory to `sys.path` from application code.
- Keep both supported entry points working:
  `import inventory_tool` and `python -m inventory_tool`.
- Importing a library module should not write to stdout or stderr.

The test harness supplies `PYTHONPATH` to model an installed or otherwise
configured package. Your implementation should only be responsible for imports
*within* that package.

## Import model: the short version

### Modules, packages, and search paths

A module is usually one `.py` file. A package is a directory of modules, with
`__init__.py` providing the package's initialization code. To import
`inventory_tool`, Python searches each directory in `sys.path` for a module or
package with that top-level name. The directory *containing* `inventory_tool`
must therefore be searchable.

Imports within a package can name a top-level module or be relative to the
current package. Python resolves the latter from the module's package context,
stored in `__package__`.

### Files versus modules

Running `python path/to/tool.py` executes a file as `__main__`. Running
`python -m package` first resolves a package through the import system, then
executes its `__main__.py`. The latter preserves package context, so relative
imports behave consistently.

### Import execution and cycles

An import executes a module's top-level statements once, then caches the module
in `sys.modules`. During that first execution, the cached module can be only
partially initialized. If module A imports B while B immediately imports a name
from A, that name may not exist yet.

Type annotations can create such a runtime dependency even when the annotated
class is not otherwise needed at runtime. Part of the diagnosis is deciding
which dependencies the running program genuinely needs.

For runnable demonstrations using temporary packages and fresh interpreters,
see [Guide 13](../../guides/13_imports_packages_and_execution.py).

## Bugs: 3

If you get stuck, open [HINTS.md](HINTS.md). It progresses from diagnostic
prompts to specific edits, so read only as far as you need.

## Discussion Questions

Return to these after the tests pass.

1. Why can `python inventory_tool/__main__.py` behave differently from
   `python -m inventory_tool`?
2. Why is changing `sys.path` inside `__main__.py` a brittle repair?
3. How can a type checker see a dependency that the running program should not
   load?
4. When would moving shared protocols or data types into a third module be
   better than guarding a type-only import?
5. Why do the tests use a fresh interpreter for each import order?
