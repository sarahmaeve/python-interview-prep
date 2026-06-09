# Exercise 33: Capstone — Multi-Module Order Pipeline

Every other exercise in this repo is a single file. Real interview codebases aren't. This capstone is a small order-processing app spread across **five modules**, with **5 bugs** — roughly one per module. Each bug is a pattern you've already met in an earlier exercise; the twist is that the *symptom* often shows up in a different module than the *cause*.

**This exercise practices:** navigating unfamiliar multi-module code, following data across module boundaries, and resisting the urge to "fix" the module a failing test happens to name.

## The modules

| Module | Role |
|---|---|
| `models.py` | `Product` (frozen dataclass) and `Order` (mutable lines + status) |
| `catalog.py` | Product lookup by SKU — case-insensitive by contract |
| `billing.py` | Decimal invoice math; pricing problems must raise, never mis-price |
| `fulfillment.py` | Orchestration: validate → charge → decrement stock → stamp status |
| `reporting.py` | Revenue and daily summaries over processed orders |

## How to run the tests

```bash
cd exercises/33_capstone_order_pipeline
python3 -m unittest test_order_pipeline -v
```

Your goal: edit the five modules until all 17 tests pass. Do **not** modify the test file.

## Suggested approach (this is the skill being practiced)

1. Run the suite and **list** the failures before touching anything.
2. For each failure, trace the data: which module produced the wrong value, and which module handed it bad input? An end-to-end failure in `reporting` can be caused two modules upstream.
3. Fix one bug at a time and re-run. Watch which *other* failures disappear with it — that tells you which symptoms shared a cause.

## Bugs: 5

<details>
<summary>Hint 1 (gentle)</summary>

One bug per module. Each one echoes an earlier exercise in this repo — if a failure feels familiar, it is. Two of the seven failing tests are downstream symptoms of bugs in *other* modules.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

- Two fresh `Order`s are sharing something they shouldn't (you saw this in exercise 06).
- `Catalog.register` and `Catalog.get` don't agree on how a SKU is spelled (a contract violation like exercise 05's spec-reading).
- `billing.order_subtotal` survives an unknown SKU when its own docstring says it must not (exercise 07/21's swallowed exceptions — with money on the line).
- Compare what `fulfillment` stamps on a confirmed order with the `CONFIRMED` constant — *character by character* (exercise 25).
- `reporting.revenue_by_customer` handles a repeat customer the way exercise 11's totals handled repeat products.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **models.py** — `Order.__init__(self, ..., lines=[])`: the mutable default is shared by every order created without explicit lines. Use a `None` sentinel and copy: `self.lines = list(lines) if lines is not None else []`.
2. **catalog.py** — `register()` stores keys upper-cased but `get()` looks up the raw string. Fix: `return self._by_sku.get(sku.upper())`.
3. **billing.py** — the `try/except (AttributeError, TypeError): continue` silently skips lines whose `catalog.get()` returned None. Replace it with an explicit check that raises `ValueError(f"unknown SKU: {sku!r}")`.
4. **fulfillment.py** — `order.status = "confirmed "` has a trailing space; nothing downstream ever matches it. Use the module's own constant: `order.status = CONFIRMED`.
5. **reporting.py** — `revenue[email] = order_subtotal(...)` overwrites a repeat customer's earlier orders. Accumulate: `revenue[email] = revenue.get(email, Decimal("0")) + order_subtotal(...)`.

</details>

## After you finish

- Which failing test did you chase into the *wrong* module first? What clue would have redirected you sooner?
- Bug 4 would have been impossible with a `StrEnum` status (exercise 25), and bug 1 impossible with a frozen dataclass + `default_factory` (exercise 23). Practice saying *why* in one sentence each — "what would you change so this class of bug can't recur" is a classic interview follow-up.
