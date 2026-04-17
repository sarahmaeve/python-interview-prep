# Solution: Exercise 25 — Enum State Machine

## Bugs Found

1. **`_VALID_TRANSITIONS[PENDING]` contains `"payed"`** — a typo. The intended value is `PAID` (the constant) — the string `"paid"`. As a result, the `pending → paid` transition silently fails with `ValueError`, while the typo-allowed `pending → payed` transition would succeed (if anyone called it).

2. **`is_terminal` compares against `"cancelled "`** (with a trailing space). No real order ever has that status, so `is_terminal()` returns `False` for every cancelled order.

3. **`summarize_orders` initialises its summary dict with the key `"Cancelled"`** (capital C) instead of `CANCELLED` (lowercase). Summarising any list containing a cancelled order raises `KeyError` at `summary[order.status] += 1`.

## Diagnosis Process

- `test_pending_to_paid` fails with a `ValueError`, pointing directly at `_VALID_TRANSITIONS[PENDING]`.
- `test_cancelled_is_terminal` returns `False`. The only way to produce `False` for a cancelled order is if the comparison misses — inspect the string literal.
- `test_single_cancelled_order` fails with `KeyError: 'cancelled'`. That error message is the tell: the key the code is trying to read differs from the key it inserted.

## The Fix

### Bug 1 — `"payed"` typo

```python
_VALID_TRANSITIONS: dict[str, set[str]] = {
    PENDING:   {PAID, CANCELLED},
    PAID:      {SHIPPED, CANCELLED},
    SHIPPED:   {DELIVERED},
    DELIVERED: set(),
    CANCELLED: set(),
}
```

### Bug 2 — trailing space in `is_terminal`

```python
def is_terminal(self) -> bool:
    return self.status in (DELIVERED, CANCELLED)
```

### Bug 3 — capitalisation in summary dict

```python
summary = {
    PENDING: 0,
    PAID: 0,
    SHIPPED: 0,
    DELIVERED: 0,
    CANCELLED: 0,
}
```

## Why This Bug Matters

Every one of these bugs becomes impossible when you refactor the status strings into a `StrEnum`:

```python
from enum import StrEnum

class OrderStatus(StrEnum):
    PENDING   = "pending"
    PAID      = "paid"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

With that in place:

- `OrderStatus.PAYED` raises `AttributeError` at import time — bug 1 never loads.
- Membership checks use enum members: `self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)`. There's no string literal to mistype.
- The summary dict uses enum members as keys, and `summary[order.status] += 1` can't miss because `order.status` IS an `OrderStatus`.

## The Recommended Refactor

```python
from enum import StrEnum

class OrderStatus(StrEnum):
    PENDING   = "pending"
    PAID      = "paid"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

_VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING:   {OrderStatus.PAID, OrderStatus.CANCELLED},
    OrderStatus.PAID:      {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED:   {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}

@dataclass
class Order:
    order_id: str
    status: OrderStatus = OrderStatus.PENDING
    history: list[OrderStatus] = field(default_factory=list)

    def is_terminal(self) -> bool:
        return self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)
```

The tests still pass because `StrEnum` members ARE strings — `OrderStatus.PAID == "paid"` is `True`, and `json.dumps({"status": order.status})` serialises as `"paid"`.

## Discussion

- The story this exercise tells is the case FOR stricter types. Every bug is the kind that slips past code review because the string literal LOOKS right. `StrEnum` moves the check to import time — where it should be.
- For state machines specifically, pattern-matching + `typing.assert_never` (Guide 10, Section 8) gives you *exhaustiveness* too: add a new status member and mypy flags every `match` that doesn't handle it.
- If the statuses in your system cross a wire (JSON field, HTTP header, DB column), `StrEnum` is ideal because its values serialise without ceremony. Plain `Enum` requires `.value` at every boundary.
