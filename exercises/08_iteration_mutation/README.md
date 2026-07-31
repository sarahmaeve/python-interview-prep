# Exercise 08: Iteration and Mutation

## Overview

You are given a `TaskManager` class that manages a list of task
dictionaries. The module has **3 bugs**, all related to common pitfalls
around iterating over and mutating collections in Python.

## Your Task

Run the tests with:

```bash
python3 -m unittest test_task_manager
```

All tests are correct. Fix the bugs in `task_manager.py` until every test passes.

## Principle Primer

Iteration assumes the underlying sequence remains structurally stable; removing
items from a list while advancing through it can skip elements. Compare values
using representations whose ordering matches their meaning—display-formatted
dates often do not. Finally, remember that iterators and generators are
one-shot streams: after consumption, they do not rewind themselves.

If you get stuck, use [HINTS.md](HINTS.md).
