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

## Principle Primer

Catch only exceptions you can meaningfully handle. A broad handler can convert
programming errors into silent data loss. When translating an exception,
preserve the public exception type and a useful message, and consider exception
chaining when the original cause helps diagnosis. If a layer cannot recover,
letting the exception propagate is usually the honest contract.

If you get stuck, use [HINTS.md](HINTS.md).
