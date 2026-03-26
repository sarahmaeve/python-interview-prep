# Exercise 21: Library Catalog

## Problem

You are building a simple library catalog system. Design classes that model books, members, and the library using composition and OOP principles.

This exercise practices: **class design, `@property`, `__eq__`/`__repr__`, composition, encapsulation (defensive copying)**.

## Constraints

- Books should be value objects (two books with the same ISBN are equal)
- Members can check out and return books
- The Library manages the collection and tracks which member has which book
- Return copies of internal state, not direct references
- No external libraries

## Your Task

Open `catalog.py` and implement each class. The docstrings and method signatures describe the expected behavior.

Run the tests to check your progress:

```bash
python3 -m unittest test_catalog
```

## Class Responsibilities

| Class | Responsibility |
|-------|---------------|
| `Book` | Value object; equality and hashing based on ISBN |
| `Member` | Tracks which books a member currently has checked out |
| `Library` | Manages the collection; handles checkout/return logic |

## Hints (only if you're stuck)

<details>
<summary>Hint 1 — Book equality and hashing</summary>
When you override `__eq__`, Python sets `__hash__` to `None` unless you also define it. Since equality is based on ISBN, hash should be too: `hash(self.isbn)`.
</details>

<details>
<summary>Hint 2 — Defensive copying</summary>
In `Member.checked_out`, return `list(self._checked_out)` (or a slice) so callers can't modify the member's internal list directly.
</details>

<details>
<summary>Hint 3 — Library internals</summary>
Consider keeping a dict mapping `isbn -> Book` for the collection, and a dict mapping `member_id -> Member` for registered members. A separate set or dict of checked-out ISBNs makes `available_books` straightforward.
</details>
