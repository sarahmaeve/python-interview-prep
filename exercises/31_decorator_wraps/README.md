# Exercise 31: Decorator `@wraps` and State

Three decorators each violate part of their public contract. The implementation
has **3 bugs** involving metadata or state.

## How to run the tests

```bash
cd exercises/31_decorator_wraps
python3 -m unittest test_decorators
```

Your goal is to edit `decorators.py` until all tests pass. Do **not** modify the test file.

## Decorators under test

- `@log_calls` — logs entry/exit of each call.
- `@retry(n)` — retries on exception up to n attempts.
- `@count_calls` — class-based decorator that counts how many times each decorated function is called.

## Principle Primer

A decorator should preserve the wrapped callable's identity for introspection,
documentation, and frameworks that inspect signatures. In a parameterized
decorator, distinguish the configuration layer, the function-accepting layer,
and the actual call wrapper. Class-based decorators are objects, so decide
whether state belongs to each decorated instance or is intentionally shared.

If you get stuck, use [HINTS.md](HINTS.md).

## Relevant reading

- `guides/11_context_and_decorators.py` — Sections 5–8 (decorator basics, `wraps`, parameterised decorators, class decorators)
