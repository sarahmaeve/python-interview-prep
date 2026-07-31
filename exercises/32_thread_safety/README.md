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

- In a standard GIL-enabled CPython build, the **GIL** allows only one thread
  to execute Python bytecode at a time. Free-threaded CPython builds can disable
  it. Neither model makes a multi-step application operation atomic: other
  threads can observe state between your “read,” “decide,” and “write.”
- Any **read-modify-write** of shared state (`x = x + 1`, "check stock, then decrement") can interleave with another thread doing the same thing. Both read the old value; one update is lost.
- A `threading.Lock` makes a block exclusive. The idiom is:

  ```python
  with self._lock:
      ...  # read, decide, and write as one atomic step
  ```

  `with` guarantees the lock is released even if the block raises — the same guarantee context managers give file handles (guide 11).
- The tests shrink `sys.setswitchinterval` so the interpreter switches threads very frequently. That makes interleavings that might take a week of production traffic to bite show up on every test run.

There are 3 bugs. If you get stuck, use [HINTS.md](HINTS.md).

For the evolving CPython execution model, see the
[official free-threading guide](https://docs.python.org/3/howto/free-threading-python.html).

For a runnable treatment of locks, queues, ownership, and deterministic
concurrency tests, see
[Guide 14](../../guides/14_threading_and_shared_state.py).

## Discussion Questions

After fixing the bugs, practice articulating these — they're standard interview territory:

1. **"Doesn't the GIL make this safe?"** What exactly does the GIL guarantee, and what doesn't it? Why did the bare `x = x + 1` race become *harder* to trigger on modern CPython, and why does it come back the moment there's a function call between the read and the write?
2. **Lock granularity**: one lock for the whole office vs. one per field. What does the coarse lock cost? When would you split it, and what new bug becomes possible once there are two locks?
3. **Alternatives to locking**: how would you redesign `TicketOffice` around a `queue.Queue` so only one thread owns the state? When is that cleaner than locks?
4. **Detecting these bugs**: the tests force frequent thread switches to make races reproducible. How would you catch this class of bug in production code review, where you can't rely on a failing test?
