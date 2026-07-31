# Exercise 25: Enum State Machine

An order lifecycle implemented with plain string constants. The implementation
has **3 bugs** involving inconsistent status representation.

## How to run the tests

```bash
cd exercises/25_enum_state_machine
python3 -m unittest test_order_state
```

Your goal is to edit `order_state.py` until all tests pass. Do **not** modify the test file.

## The state machine

```
    pending ──▶ paid ──▶ shipped ──▶ delivered
        │        │
        └──▶ cancelled ◀──┘
```

- `transition(new_status)` moves to a new status or raises `ValueError`.
- `is_terminal()` — true when the order can't transition any further.
- `is_active()` — true while the order is still in flight.
- `summarize_orders(list)` — `{status: count}` across a batch.

## Principle Primer

String sentinels create an informal vocabulary that every comparison must spell
identically. An enum makes that vocabulary explicit, but it prevents these bugs
only when the model consistently stores enum members and code refers to those
members rather than continuing to use raw strings. Values arriving from JSON,
a database, or user input still need validation at the boundary.

If you get stuck, use [HINTS.md](HINTS.md). The canonical solution also
discusses a `StrEnum` refactor after repairing the existing design.

## Relevant reading

- `guides/02_classes_and_oop.py` — Section 10 (Enum / StrEnum)
- `guides/09_modern_data_types.py` — Section 4 (StrEnum in depth)
