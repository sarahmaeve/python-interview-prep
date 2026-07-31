# Exercise 04: Inheritance Bugs — Shapes Hierarchy

A small hierarchy of shape classes: `Shape`, `Rectangle`, `Square`, and `Circle`.

## Your Task

The file `shapes.py` contains **3 bugs**. Run the tests with:

```bash
python3 -m unittest test_shapes
```

All 10 tests should pass once every bug is fixed. Read the test file to understand the expected behavior, find the bugs, and fix them.

## Principle Primer

A subclass inherits behavior that may depend on parent-owned state. If the
subclass introduces another name for the same concept, updates must keep those
representations synchronized—or, better, retain one source of truth. Also
distinguish a bound method object from the result of calling it:
`obj.method` and `obj.method()` are different values.

If you get stuck, use [HINTS.md](HINTS.md).
