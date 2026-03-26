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

- **Python 3.8+** (standard library only — no pip installs required)

## How to Use

### 1. Read the Guides

Start with the `guides/` directory. Each file is a heavily commented, runnable Python script covering a core topic:

| # | Guide | Topic |
|---|-------|-------|
| 1 | `01_functions_and_scope.py` | Functions, arguments, scope, closures |
| 2 | `02_classes_and_oop.py` | Classes, instance vs class attributes, inheritance |
| 3 | `03_unittest_fundamentals.py` | unittest framework, assertions, test structure |
| 4 | `04_debugging_strategies.py` | Systematic debugging, reading tracebacks |
| 5 | `05_mocking_and_external_deps.py` | unittest.mock, patching, testing external dependencies |
| 6 | `06_clean_code_principles.py` | Naming, structure, readability, code smells |
| 7 | `07_type_hinting.py` | Type annotations, mypy, catching bugs with types |

Run any guide to see its demonstrations:

```bash
python guides/01_functions_and_scope.py
```

### 2. Work Through the Exercises

The `exercises/` directory contains 12 debug exercises in progressive difficulty. Each exercise has:

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
