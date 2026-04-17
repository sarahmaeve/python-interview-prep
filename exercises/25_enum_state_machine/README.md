# Exercise 25: Enum State Machine

An order lifecycle implemented with plain string constants. The implementation has **3 bugs** — each is a string typo that a `StrEnum` would have caught at import time.

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

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

Every bug is a string that doesn't match one of the five defined constants (`PENDING`, `PAID`, `SHIPPED`, `DELIVERED`, `CANCELLED`). Look for: typos, trailing whitespace, and wrong capitalisation. Compare each string literal to the named constants at the top of the file.

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `_VALID_TRANSITIONS[PENDING]` allows a transition to a string that looks *almost* like one of the constants.
2. `is_terminal` has a whitespace issue.
3. `summarize_orders`'s summary dict has a mis-capitalised key.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `_VALID_TRANSITIONS[PENDING]` uses `"payed"` (should be `PAID`).
2. `is_terminal` compares against `"cancelled "` (trailing space; should be `CANCELLED`).
3. `summarize_orders` initialises the summary with the key `"Cancelled"` (capital C; should be `CANCELLED`).

</details>

## Discussion

Every bug here disappears the moment you refactor to a `StrEnum`:

```python
from enum import StrEnum

class OrderStatus(StrEnum):
    PENDING   = "pending"
    PAID      = "paid"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

With that in place, `OrderStatus.PAYED` raises `AttributeError` at import time. You never ship the typo to production because the module won't load.

The solution walkthrough shows both: fixing the bugs in place (what the tests verify), and the recommended refactor to `StrEnum`.

## Relevant reading

- `guides/02_classes_and_oop.py` — Section 10 (Enum / StrEnum)
- `guides/09_modern_data_types.py` — Section 4 (StrEnum in depth)
