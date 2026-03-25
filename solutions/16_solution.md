# Solution 16 --- Fixing Mock Bugs in `test_inventory_service.py`

## Bug 1: Wrong Patch Target (line 106)

**Location:** `TestFetchSupplierPrice.test_fetch_supplier_price`

**What's wrong:** The decorator patches `urllib.request.urlopen` -- the original definition site. But `inventory_service.py` already imported `urlopen` into its own namespace. The production code calls its *local* reference, which the patch never touched.

**Error you'd see:** `URLError` or `NotImplementedError` -- the real `urlopen` runs and tries to hit the network.

**Fix:**

```python
# Before
@patch("urllib.request.urlopen")

# After
@patch("inventory_service.urlopen")
```

**Lesson:** Always patch where the name is *looked up*, not where it is *defined*. If a module does `from X import Y`, patch `module.Y`, not `X.Y`.

---

## Bug 2: Typo Hidden by Missing `spec` (line 136)

**Location:** `TestRestock.test_restock_calls_execute`

**What's wrong:** The assertion checks `mock_db.exceute.called` (note the typo: "exceute" instead of "execute"). Because the mock was created without `spec=Database`, accessing `.exceute` silently creates a new attribute that was never called -- so `.called` is `False` and the assertion fails.

**Error you'd see:** `AssertionError: False is not true` -- the test thinks `execute` was never called, but in reality it was called (just under the correct spelling).

**Fix:**

```python
# Before
mock_db = MagicMock()  # no spec
...
self.assertTrue(mock_db.exceute.called)

# After
mock_db = MagicMock(spec=Database)
...
self.assertTrue(mock_db.execute.called)
```

Adding `spec=Database` would have caught the typo immediately with an `AttributeError`. Fixing the spelling completes the repair.

**Lesson:** Always use `spec=` on mocks. Without it, any attribute access silently succeeds, and typos become invisible.

---

## Bug 3: Wrong Return Type from Mock (line 144)

**Location:** `TestGetStockWithTimestamp.test_get_stock_with_timestamp`

**What's wrong:** `mock_time.return_value` is set to a plain string `"2026-03-25T10:00:00"`. But the production code calls `now.isoformat()` on the return value. A string has no `.isoformat()` method (well, it does not return what you expect -- it would call `str.isoformat` which does not exist and raises `AttributeError`).

**Error you'd see:** `AttributeError: 'str' object has no attribute 'isoformat'`

**Fix:**

```python
# Before
mock_time.return_value = "2026-03-25T10:00:00"

# After
mock_time.return_value = datetime(2026, 3, 25, 10, 0, 0)
```

**Lesson:** A mock's return value must match the *type* the production code expects. If the code calls `.isoformat()` on the result, you must return an object that has that method -- a real `datetime`, not a string.

---

## Bug 4: Stacked `@patch` Decorators with Swapped Arguments (line 159-161)

**Location:** `TestShouldReorder.test_should_reorder_checks_price`

**What's wrong:** When stacking `@patch` decorators, they are applied bottom-up, so the parameters are passed *innermost decorator first*. The bottom decorator is `@patch.object(InventoryService, "get_stock")`, so its mock is the **first** parameter. The top decorator is `@patch.object(InventoryService, "fetch_supplier_price")`, so its mock is the **second** parameter. The test names them `mock_fetch, mock_stock` -- but that assigns `get_stock`'s mock to `mock_fetch` and `fetch_supplier_price`'s mock to `mock_stock`. The return values are then set on the wrong mocks.

**Error you'd see:** `should_reorder` returns `False` because `get_stock` returns `29.99` (not `< 5`) or the logic otherwise breaks.

**Fix:**

```python
# Before
def test_should_reorder_checks_price(self, mock_fetch, mock_stock):

# After
def test_should_reorder_checks_price(self, mock_stock, mock_fetch):
```

**Lesson:** Stacked `@patch` decorators pass mocks in bottom-up order. The bottommost decorator's mock is the first positional argument after `self`. Name your parameters to match.

---

## Mock Debugging Checklist

When a mock-based test fails unexpectedly, work through these checks:

1. **Patch target correct?** If you `from X import Y`, patch `your_module.Y`, not `X.Y`.
2. **Using `spec=`?** Without it, typos in method names silently succeed. Add `spec=RealClass` and see if an `AttributeError` reveals a typo.
3. **Return type realistic?** If production code calls methods on the return value (`.isoformat()`, `.read()`, `.decode()`), the mock must return an object that supports those methods.
4. **Stacked decorators ordered correctly?** Bottom `@patch` maps to the first arg after `self`. Read the decorator stack bottom-to-top when naming parameters.
5. **`side_effect` vs `return_value`?** Use `side_effect` for exceptions or sequences; use `return_value` for a single fixed result. Setting both can cause confusion -- `side_effect` takes priority.
6. **Asserting the right mock?** After a test fails, add `print(mock.call_args_list)` to verify calls actually landed where you expected.
