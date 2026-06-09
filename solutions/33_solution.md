# Solution: Exercise 33 — Capstone (Order Pipeline)

## Bugs Found

1. **models.py — shared mutable default.** `Order.__init__(..., lines=[])` evaluates the empty list once, at function definition; every order created without explicit lines shares it. `add_line` on one order shows up on all of them. (Exercise 06's bug, in dataclass-free form.)

2. **catalog.py — asymmetric normalisation.** `register()` stores keys as `sku.upper()`, but `get()` looks up the raw string. The docstring promises case-insensitive lookup; `get("cof-1")` returns None for a product registered as `"COF-1"`.

3. **billing.py — swallowed pricing failure.** `order_subtotal` wraps `line_total` in `except (AttributeError, TypeError): continue`. When `catalog.get()` returns None for an unknown SKU, `line_total(None, qty)` raises AttributeError — and the line is silently priced at zero. The docstring requires a ValueError instead.

4. **fulfillment.py — status sentinel typo.** A confirmed order is stamped `"confirmed "` (trailing space) instead of the module's own `CONFIRMED` constant. Every downstream comparison — reporting filters, the daily summary — silently fails to match.

5. **reporting.py — overwrite instead of accumulate.** `revenue_by_customer` assigns `revenue[email] = order_subtotal(...)`, so a repeat customer's earlier orders are replaced rather than summed. (Exercise 11's totals bug.)

## Diagnosis Process — following symptoms across modules

The instructive part of this exercise is that two failures point away from their causes:

- `test_lowercase_sku_order_is_confirmed` fails in **fulfillment** (order REJECTED) — but fulfillment is doing its job. It asked the **catalog** for `"cof-1"` and was told the product doesn't exist. The fix belongs in `catalog.get`, not in `place_order`.
- `test_daily_summary_counts_fulfilled_orders` fails in **reporting** ({"confirmed": 0, "rejected": 2}) — but `daily_summary` is correct. The order it received was stamped `"confirmed "` upstream in **fulfillment**. Printing `order.status!r` (with the `!r`!) makes the trailing space visible instantly; printing without `repr` hides it.

The other three failures are local: the models test fails inside models, the billing test inside billing, the revenue test inside reporting.

A productive order of attack: fix the local ones first (1, 3, 5), then chase the two cross-module ones (2, 4). Re-running after each fix shows which symptoms shared a cause.

## The Fixes

```python
# models.py
def __init__(self, order_id, customer_email, lines=None):
    self.order_id = order_id
    self.customer_email = customer_email
    self.lines = list(lines) if lines is not None else []
```

(`list(lines)` also defensively copies a caller-supplied list — guide 02 §8.)

```python
# catalog.py
def get(self, sku):
    return self._by_sku.get(sku.upper())
```

```python
# billing.py
for sku, quantity in order.lines:
    product = catalog.get(sku)
    if product is None:
        raise ValueError(f"unknown SKU: {sku!r}")
    total += line_total(product, quantity)
```

```python
# fulfillment.py
order.status = CONFIRMED
```

```python
# reporting.py
revenue[order.customer_email] = (
    revenue.get(order.customer_email, Decimal("0"))
    + order_subtotal(catalog, order)
)
```

## Why These Bugs Matter

- **Symptom-module ≠ cause-module** is the defining feature of real debugging. The failing test names `fulfillment`; the bug lives in `catalog`. Interviewers watch for whether you read the failing assertion and then *follow the data*, or just start editing the file the test imports.
- **Normalise at one boundary.** The catalog normalises on write but not on read. Pick a rule — "keys are normalised at every entry point" — and apply it symmetrically. Asymmetric normalisation is a whole bug family (emails, usernames, paths, headers).
- **Money code must fail loudly.** Bug 3 produced *cheaper invoices*, not exceptions. Nobody files a ticket for being undercharged; this class of bug survives in production for years. `except: continue` around pricing is the single scariest line in this exercise.
- **Sentinel strings rot.** A trailing space defeated every status comparison in the system, invisibly. The structural fix — covered in exercise 25 — is a `StrEnum`, which makes the typo an `AttributeError` at import time instead of a silent mismatch at report time.

## Hardening discussion (interview follow-up material)

Each bug has a "make it impossible" refactor, and naming them is interview gold:

| Bug | Structural prevention |
|---|---|
| Shared default lines | `@dataclass` with `field(default_factory=list)` (ex 23) |
| Case asymmetry | Normalise in ONE private helper used by both register and get |
| Swallowed pricing error | No bare/broad excepts in money paths; raise domain errors (ex 07) |
| Status typo | `StrEnum` for the status lifecycle (ex 25) |
| Overwrite vs accumulate | `collections.Counter` / `defaultdict(Decimal)` for aggregation |
