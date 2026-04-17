# Python Interview Prep

A hands-on preparation tool for Python interviews focused on **debugging**, **test-driven reasoning**, and **code comprehension**.

This is **not** an algorithm drill or LeetCode substitute. The exercises here mirror a real interview format: you'll be given an existing codebase with unit tests, and your job is to read, debug, and fix the code.

## Skills Practiced

- Reading and understanding unfamiliar code
- Systematically diagnosing issues within a test-driven workflow
- Articulating your thought process and trade-offs
- Writing clear, maintainable code

## Short on Time?

See **[STUDY_GUIDE.md](STUDY_GUIDE.md)** for prioritized 2-hour, 4-hour, and full-day prep tracks.

## Prerequisites

- **Python 3.11+** — the guides and exercises use idioms introduced in 3.10 (`match`/`case`, `X | None`) and 3.11 (`StrEnum`, `typing.Self`, `assert_never`, `asyncio.timeout`, `asyncio.TaskGroup`, `ExceptionGroup`).
- **Standard library only** for the exercise code.
- **Dev dependencies** (pytest, mypy, ruff) are optional — install them if you want to run exercise 30 (pytest translation), type-check yourself, or lint:

  ```bash
  pip install pytest mypy ruff
  # or, on pip 25+ / uv:
  pip install --group dev
  ```

## Run everything

From the repo root:

```bash
make test         # runs every exercise test via unittest discovery
make test-guides  # runs every guide (each is self-verifying)
make check        # lint + typecheck + tests (what CI runs)
```

Without the Makefile (each exercise is its own standalone package — discovery is per-directory):

```bash
# Run all exercises:
for d in exercises/*/; do (cd "$d" && python -m unittest discover -p "test_*.py"); done

# Or run one exercise:
cd exercises/08_iteration_mutation && python -m unittest
```

Pytest, by contrast, can discover from the root:

```bash
python -m pytest exercises  # requires pytest installed
```

## How to Use

### 1. Read the Guides

Start with the `guides/` directory. Each file is a heavily commented, runnable Python script covering a core topic:

| #  | Guide | Topic |
|----|-------|-------|
| 1  | `01_functions_and_scope.py`         | Functions, arguments, scope, closures, generators |
| 2  | `02_classes_and_oop.py`             | Classes, inheritance, `@dataclass`, `StrEnum`, `@cached_property` |
| 3  | `03_unittest_fundamentals.py`       | unittest framework, `subTest`, pytest translation cheat sheet |
| 4  | `04_debugging_strategies.py`        | Systematic debugging, tracebacks, `logging.exception` |
| 5  | `05_mocking_and_external_deps.py`   | `unittest.mock`, patching, `AsyncMock` |
| 6  | `06_clean_code_principles.py`       | Naming, structure, readability, code smells |
| 7  | `07_type_hinting.py`                | Type annotations, `Self`, `NotRequired`, `assert_never`, mypy |
| 8  | `08_observability_and_systems.py`   | Logging, instrumentation, env config, CI/CD |
| 9  | `09_modern_data_types.py`           | `@dataclass` (frozen/slots/kw_only), `StrEnum`, `Decimal` |
| 10 | `10_paths_and_matching.py`          | `pathlib`, `match`/`case`, exhaustiveness via `assert_never` |
| 11 | `11_context_and_decorators.py`      | Context managers, `@contextmanager`, decorators, `functools.wraps` |
| 12 | `12_async_and_testing.py`           | asyncio, `TaskGroup`, `asyncio.timeout`, `AsyncMock` |

Run any guide to see its demonstrations:

```bash
python guides/01_functions_and_scope.py
```

### 2. Work Through the Exercises

The `exercises/` directory contains debug and integration exercises in progressive difficulty. Each exercise has:

- **`README.md`** — Context, instructions, and hints
- **`<module>.py`** — A buggy implementation (this is what you fix)
- **`test_<module>.py`** — Correct unit tests (do not modify these)

Your goal: **read the tests, understand the intended behavior, find and fix the bugs, then run the tests until they all pass.**

```bash
cd exercises/01_basic_functions
python -m unittest test_shopping_cart
```

### 3. Check Solutions

After attempting an exercise, check `solutions/` for a walkthrough of the diagnosis process. Solutions are written as explanations, not corrected code — the goal is to practice the reasoning, not copy an answer.

## Exercise Map

### Beginner

| # | Exercise | Topic Areas | Bugs |
|---|----------|-------------|------|
| 01 | Shopping Cart | Functions, reading tests | 3 |
| 02 | Text Formatter | String manipulation, edge cases | 3 |
| 03 | Bank Account | Classes, instance vs class attributes | 3 |
| 04 | Shapes | Inheritance, `super()` | 3 |

### Intermediate

| # | Exercise | Topic Areas | Bugs |
|---|----------|-------------|------|
| 05 | User Validator | Reading tests as a spec | 4 |
| 06 | Event Logger | Mutable defaults, shallow copy | 3 |
| 07 | Config Parser | Exception handling anti-patterns | 3 |
| 08 | Task Manager | Iteration/mutation, generators | 3 |

### Advanced

| # | Exercise | Topic Areas | Bugs |
|---|----------|-------------|------|
| 09 | Weather Client | Mocking external APIs | 3 |
| 10 | Cache with Expiry | Time-dependent bugs, intermittent failures | 3 |
| 11 | CSV Report | File I/O, resource management | 3 |
| 12 | Notification Service | Refactoring for testability (capstone) | 4 |

### Type Hinting

| # | Exercise | Topic Areas | Goal |
|---|----------|-------------|------|
| 13 | Grade Processor | Bugs preventable by type hints | Fix 4 bugs that mypy would have caught |
| 14 | Task Registry | Adding type annotations | Add type hints to working code (tests verify annotations) |

### Mocking

| # | Exercise | Topic Areas | Goal |
|---|----------|-------------|------|
| 15 | Payment Processor | Writing mocks from scratch | Fill in TODO mock setups to make 10 tests pass |
| 16 | Inventory Service | Fixing broken test mocks | Fix 4 mock-related bugs in the test file |

### OOP Patterns

| # | Exercise | Topic Areas | Goal |
|---|----------|-------------|------|
| 17 | Temperature Monitor | `@property`, composition | Fix 4 bugs with properties and composition |

### Write Tests from Scratch

| # | Exercise | Topic Areas | Goal |
|---|----------|-------------|------|
| 18 | String Calculator | Writing tests, edge cases | Write a test suite for working code |
| 19 | Order Service | Writing tests with mocks | Write tests for code with external dependencies |

### Black Box / Observability / Systems

| # | Exercise | Topic Areas | Goal |
|---|----------|-------------|------|
| 20 | Black Box Wrapper | Adapter pattern, introspection, opaque dependencies | Fix 3 bugs in a wrapper around an unmodifiable module |
| 21 | Observability & Logging | `logging` module, `assertLogs`, instrumentation | Fix 3 bugs to make a processor log meaningful warnings |
| 22 | Systems Integration | Environment config, timeouts, retries, CI/CD | Fix 3 bugs related to deployment environment interaction |

### Modern Python Idioms (3.11+)

| # | Exercise | Topic Areas | Goal |
|---|----------|-------------|------|
| 23 | Dataclass Refactor | `@dataclass(frozen)`, `field(default_factory)`, `dataclasses.replace` | Fix 4 bugs in a value-object class |
| 24 | Money and Decimal | `Decimal` vs `float`, rounding rules, precision | Fix 3 bugs in an invoice calculator |
| 25 | Enum State Machine | `StrEnum`, string-sentinel typos | Fix 3 typo bugs in a status state machine |
| 26 | pathlib Bugs | `pathlib`, compound suffixes, `rglob`, hidden paths | Fix 3 bugs in a backup tool |
| 27 | match/case Dispatch | `match`/`case`, mapping patterns, exhaustiveness | Fix 3 bugs in an event router |
| 28 | Context Manager Leaks | `__enter__`/`__exit__`, `@contextmanager`, try/except/else | Fix 3 cleanup-path bugs |
| 29 | Async Retry | asyncio, `await`, `AsyncMock`, `asyncio.timeout` | Fix 3 async-specific bugs in a retry client |
| 30 | Pytest Translation | unittest → pytest idioms | Translate a unittest suite into pytest |
| 31 | Decorator `@wraps` | `functools.wraps`, parameterised decorators, class decorators | Fix 3 decorator hygiene bugs |
