# Exercise 32: Thread Safety

A `TicketOffice` instance is shared by many request-handler threads. It sells tickets, restocks them, and reports sales — and under concurrent load it loses sales, sells more tickets than exist, wedges itself after a failed call, and crashes during reporting. The implementation has **3 bugs**.

**This exercise practices:** reasoning about shared mutable state, `threading.Lock`, the check-then-act race, lock hygiene on error paths, and why the GIL does *not* make your code thread-safe.

## How to run the tests

```bash
cd exercises/32_thread_safety
python3 -m unittest test_ticket_office
```

Your goal: edit `ticket_office.py` until all tests pass — **reliably**. Run the suite several times; a fix that passes "most of the time" is not a fix. Do **not** modify the test file.

## A 60-second threading primer

- The **GIL** ensures only one thread executes Python bytecode at a time. It does **not** make multi-step operations atomic: the interpreter can switch threads *between* your "read", your "decide", and your "write".
- Any **read-modify-write** of shared state (`x = x + 1`, "check stock, then decrement") can interleave with another thread doing the same thing. Both read the old value; one update is lost.
- A `threading.Lock` makes a block exclusive. The idiom is:

  ```python
  with self._lock:
      ...  # read, decide, and write as one atomic step
  ```

  `with` guarantees the lock is released even if the block raises — the same guarantee context managers give file handles (guide 11).
- The tests shrink `sys.setswitchinterval` so the interpreter switches threads very frequently. That makes interleavings that might take a week of production traffic to bite show up on every test run.

## Bugs: 3

<details>
<summary>Hint 1 (gentle)</summary>

The class creates `self._lock` in `__init__`. Which methods touch shared state without ever using it? And in the one method that *does* use it, trace what happens on every possible exit path.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `sell()` reads `self._available`, makes a decision, does some pricing work, and then writes back — with no lock held. Two threads can both pass the check for the same last ticket.
2. `restock()` calls `acquire()` and `release()` manually. What happens to the lock if the `ValueError` fires between them? Every later caller of a lock-using method will block forever.
3. `channel_report()` iterates `self._sales_by_channel` while seller threads may be inserting new keys. Iterating a dict while another thread resizes it raises `RuntimeError`.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **`sell()`**: wrap the whole body — read, check, and all writes — in `with self._lock:`. (Computing the price inside the lock is fine here; if pricing were expensive you'd compute first, then re-check inside the lock.)
2. **`restock()`**: replace the manual `acquire()`/`release()` pair with `with self._lock:`. The `with` form releases on the exception path too.
3. **`channel_report()`**: take the lock and return a copy — `with self._lock: return dict(self._sales_by_channel)`. Never hand out a live reference to state another thread mutates.

</details>

## Discussion Questions

After fixing the bugs, practice articulating these — they're standard interview territory:

1. **"Doesn't the GIL make this safe?"** What exactly does the GIL guarantee, and what doesn't it? Why did the bare `x = x + 1` race become *harder* to trigger on modern CPython, and why does it come back the moment there's a function call between the read and the write?
2. **Lock granularity**: one lock for the whole office vs. one per field. What does the coarse lock cost? When would you split it, and what new bug becomes possible once there are two locks?
3. **Alternatives to locking**: how would you redesign `TicketOffice` around a `queue.Queue` so only one thread owns the state? When is that cleaner than locks?
4. **Detecting these bugs**: the tests force frequent thread switches to make races reproducible. How would you catch this class of bug in production code review, where you can't rely on a failing test?
