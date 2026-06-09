# Solution: Exercise 32 — Thread Safety (Ticket Office)

## Bugs Found

1. **`sell()` performs check-then-act on shared state with no lock.** It reads `self._available`, decides, computes the order value (a Python function call — a point where the interpreter can switch threads), and only then writes the new value back. Two threads can both read the same `remaining`, both pass the check, and both write — one sale vanishes from the books, or the same last ticket is sold twice.

2. **`restock()` leaks the lock on its error path.** It calls `self._lock.acquire()` manually, then raises `ValueError` for negative quantities *before* `release()` ever runs. The lock stays held forever; the next call that tries to take it blocks indefinitely. One bad request wedges the whole office.

3. **`channel_report()` iterates a shared dict while sellers mutate it.** Inserting a new key from another thread while the report loop is mid-iteration raises `RuntimeError: dictionary changed size during iteration` — a crash in a read-only reporting path.

## Diagnosis Process

- `test_concurrent_sales_account_for_every_ticket` fails with `available` not matching `pool - sold`: sales are disappearing. Counter mismatches under concurrency = unsynchronized read-modify-write.
- `test_contended_sales_never_sell_more_than_the_pool` shows `total_sold + available != pool`: tickets are being created/destroyed at the boundary — the classic check-then-act race.
- `test_failed_restock_does_not_wedge_the_office` times out waiting for a follow-up call: something is still holding the lock. Whenever you see "deadlock after an exception", look for a manual `acquire()` with no `try/finally`.
- `test_channel_report_is_safe_during_concurrent_sales` errors with `RuntimeError: dictionary changed size during iteration` — the same mutation-during-iteration failure as exercise 08/10, but caused by *another thread* instead of your own loop.

## The Fix

```python
def sell(self, quantity: int = 1, channel: str = "web") -> bool:
    with self._lock:
        remaining = self._available
        if remaining < quantity:
            return False
        order_value = self._order_value(quantity)
        self._available = remaining - quantity
        self._total_sold = self._total_sold + quantity
        self._revenue = self._revenue + order_value
        sold_here = self._sales_by_channel.get(channel, 0)
        self._sales_by_channel[channel] = sold_here + quantity
        return True

def restock(self, quantity: int) -> None:
    with self._lock:
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        self._available += quantity

def channel_report(self) -> dict[str, int]:
    with self._lock:
        return dict(self._sales_by_channel)
```

The read, the decision, and every write happen as one exclusive step. `with self._lock:` releases on every exit path — normal return, early `return False`, and exceptions alike. `channel_report` returns a *copy* taken under the lock, so callers never hold a live reference to state another thread mutates (the same defensive-copy rule as guide 02 §8, with higher stakes).

## Why This Bug Matters

- **"The GIL makes Python thread-safe" is the most dangerous half-truth in Python concurrency.** The GIL serializes individual bytecodes, not your *logical* operations. Any sequence of read → decide → write can be interleaved.
- **A subtlety worth knowing for interviews:** on modern CPython (3.12+), the interpreter only considers switching threads at loop back-edges and Python function entries. A bare `self.x = self.x + 1` with nothing in between often won't race anymore — which is exactly why these bugs survive code review. The moment real code does real work between the read and the write (pricing, validation, logging — here, `_order_value()`), the switch point reappears and the race is back. Don't reason from "my toy demo didn't fail"; reason from "is this read-modify-write atomic? No."
- **Manual `acquire()`/`release()` is the `open()` without `with` of concurrency.** Any exception between the two leaks the lock, and unlike a leaked file handle, a leaked lock takes the whole process hostage — every thread that touches that lock blocks forever. This is why `with lock:` exists.
- **Reporting crashes are real outages.** The dict-iteration `RuntimeError` pattern frequently ships because reports "only read". Reading a structure that another thread is writing is still a data race.

## Discussion

- A coarser design avoids the manual bookkeeping entirely: push sale requests onto a `queue.Queue` consumed by a single owner thread — then only one thread ever touches the state and no locks are needed. Locks are the right tool here because the state is small and contention is low.
- If `sell()` needed to do something *slow* (a network price lookup), holding the lock across it would serialize all sales. The pattern then is: compute outside the lock, re-check the condition inside the lock before committing ("optimistic" check-then-act done right).
- `threading.RLock` exists for code where a lock-holding method calls another lock-taking method of the same object. With plain `Lock`, that's a self-deadlock.
- The tests make races reproducible by shrinking `sys.setswitchinterval`. The same trick is useful in real test suites for concurrency-sensitive code — far cheaper than hunting a once-a-week CI flake.
