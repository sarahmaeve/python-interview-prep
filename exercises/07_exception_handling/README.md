# Exercise 07: Exception Handling

## Overview

You are given a `ConfigParser` class that loads, stores, and retrieves
configuration values. The module has **3 bugs**, all related to exception
handling anti-patterns.

## Your Task

Run the tests with:

```bash
python3 -m unittest test_config_parser
```

All tests are correct. Fix the bugs in `config_parser.py` until every test passes.

## Bugs to Find

1. An overly broad `except` clause that swallows exceptions it should not catch.
2. An exception that is re-raised with the wrong type and a missing message.
3. An exception that is silently suppressed instead of being allowed to propagate.
