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

## Bugs to Find

1. Mutating a list while iterating over it.
2. Comparing date strings lexicographically instead of by actual date value.
3. Consuming a generator twice when it can only be iterated once.
