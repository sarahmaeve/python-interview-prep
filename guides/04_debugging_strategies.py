"""
Guide 04 — Debugging Strategies
================================

A collection of annotated "case studies" that walk through common bugs, the
thought process for diagnosing them, and systematic strategies you can apply
in interviews and real codebases.

Run this file to execute all demonstrations:

    python guides/04_debugging_strategies.py

Every case study is self-contained and prints its own output.

TABLE OF CONTENTS
  1. The systematic debugging workflow       (line ~30)
  2. Reading tracebacks                      (line ~55)
  3. Common error types and what they mean   (line ~95)
  4. Strategic print() debugging             (line ~145)
  5. Assert statements as development checks (line ~185)
  6. Binary search debugging                 (line ~215)
  7. Off-by-one errors                       (line ~245)
  8. The "it works sometimes" checklist      (line ~290)
"""


# ============================================================================
# 1. THE SYSTEMATIC DEBUGGING WORKFLOW
# ============================================================================
# When you hit a bug — especially in an interview — resist the urge to start
# changing code randomly.  Follow these steps:
#
#   1. REPRODUCE   — Can you trigger the bug reliably?  What inputs cause it?
#   2. ISOLATE     — Where in the code does the behaviour diverge from what
#                    you expect?  Narrow the search space.
#   3. DIAGNOSE    — WHY does it diverge?  Read the code; form a hypothesis.
#   4. FIX         — Make the smallest change that addresses the root cause.
#   5. VERIFY      — Run the failing test again.  Run ALL tests to make sure
#                    you didn't break something else.
#
# In an interview, narrate this process out loud.  Interviewers care as much
# about your reasoning as the final fix.


# ============================================================================
# 2. READING TRACEBACKS
# ============================================================================
# Python tracebacks read BOTTOM-TO-TOP.
#
# Example traceback:
#
#   Traceback (most recent call last):
#     File "app.py", line 40, in process_order      ← earlier caller
#       total = calculate_total(items)
#     File "app.py", line 12, in calculate_total     ← the crash site
#       price = item["price"]
#   KeyError: 'price'                                ← START reading here
#
# Step 1: Read the LAST line.  "KeyError: 'price'" tells you a dict lookup
#         failed because the key "price" doesn't exist.
# Step 2: Read the frame ABOVE it.  Line 12 in calculate_total did
#         item["price"] — so one of the items is missing a "price" key.
# Step 3: Think about WHY.  Maybe some items use "cost" instead of "price",
#         or maybe the data source occasionally omits that field.


def case_study_traceback():
    """Demonstrate catching and explaining a traceback."""
    print("=" * 60)
    print("CASE STUDY: Reading a traceback")
    print("=" * 60)

    items = [
        {"name": "Widget", "price": 9.99},
        {"name": "Gadget", "cost": 14.99},   # BUG: wrong key name
    ]

    # The buggy version would crash:
    #   total = sum(item["price"] for item in items)  → KeyError
    #
    # Diagnosis: The second dict uses "cost" not "price".
    # Fix: Use .get() with a fallback, or fix the data source, or handle
    # both key names.

    total = sum(item.get("price", item.get("cost", 0)) for item in items)
    print(f"  Items: {items}")
    print(f"  Total (after fix): {total}")
    print(f"  Lesson: When you see KeyError, check what keys actually exist.\n")


# ============================================================================
# 3. COMMON ERROR TYPES AND WHAT THEY MEAN
# ============================================================================

def case_study_common_errors():
    """Walk through the five most common exception types."""
    print("=" * 60)
    print("CASE STUDY: Common error types")
    print("=" * 60)

    # --- TypeError ---
    # "You used the wrong type."
    # Common triggers: calling a non-callable, wrong argument count,
    # concatenating str + int, passing None where a sequence is expected.
    try:
        result = "age: " + 25  # Can't concatenate str and int
    except TypeError as e:
        print(f"  TypeError: {e}")
        print(f"    Fix: use f-string or str(25)\n")

    # --- AttributeError ---
    # "That object doesn't have this attribute/method."
    # Often means the variable is a different type than you expected,
    # frequently None from a function that returned nothing.
    try:
        result = None
        result.append(1)  # None has no .append()
    except AttributeError as e:
        print(f"  AttributeError: {e}")
        print(f"    Fix: check why the variable is None — missing return?\n")

    # --- KeyError ---
    # "That key doesn't exist in the dict."
    try:
        config = {"host": "localhost"}
        port = config["port"]
    except KeyError as e:
        print(f"  KeyError: {e}")
        print(f"    Fix: use .get('port', default) or add the key\n")

    # --- ValueError ---
    # "The type is right, but the value is wrong."
    try:
        number = int("twelve")
    except ValueError as e:
        print(f"  ValueError: {e}")
        print(f"    Fix: validate input before converting\n")

    # --- IndexError ---
    # "That index is out of range."
    try:
        names = ["Alice", "Bob"]
        third = names[2]
    except IndexError as e:
        print(f"  IndexError: {e}")
        print(f"    Fix: check len() before indexing, or use try/except\n")


# ============================================================================
# 4. STRATEGIC print() DEBUGGING
# ============================================================================
# print() debugging gets a bad reputation, but it's effective when used
# strategically — especially in interviews where you can't use a full
# debugger.
#
# KEY PRINCIPLE: Narrow the search space.  Don't sprinkle print() everywhere.
# Instead, use a binary-search approach:
#   1. Print at the midpoint of the suspect code.
#   2. If the value is correct there, the bug is AFTER that point.
#   3. If it's already wrong, the bug is BEFORE that point.
#   4. Repeat until you've cornered the bug.
#
# ALWAYS label your prints.  "42" in the console means nothing.
# "balance after deposit: 42" tells you exactly where you are.

def case_study_print_debugging():
    """A function that silently gives wrong results — no crash, no traceback."""
    print("=" * 60)
    print("CASE STUDY: Strategic print() debugging")
    print("=" * 60)

    def calculate_average(grades):
        """Bug: this returns the wrong average for some inputs."""
        total = 0
        count = 0
        for grade in grades:
            if grade >= 0:       # Intended: skip negative (invalid) grades
                total += grade
                count += 1
        # BUG: if all grades are negative, count is 0 → ZeroDivisionError.
        # Also: should we skip 0 as a valid grade?  0 is >= 0, so it's kept.
        # That's probably correct, but worth questioning.
        if count == 0:
            return 0.0
        return total / count

    test_cases = [
        ([90, 80, 70], 80.0),
        ([100, -1, 90], 95.0),       # -1 is skipped
        ([-1, -2, -3], 0.0),         # All invalid
        ([0, 100], 50.0),            # 0 is a valid grade
    ]

    for grades, expected in test_cases:
        result = calculate_average(grades)
        status = "PASS" if abs(result - expected) < 0.001 else "FAIL"
        # This is what strategic print-debugging looks like: labeled values,
        # comparing actual vs expected, so you can spot the divergence.
        print(f"  {status}: grades={grades}  expected={expected}  got={result}")

    # --- Beyond print: breakpoint() ---
    # For interactive debugging, use breakpoint() (Python 3.7+).
    # It drops you into pdb where you can:
    #   p variable    — print a variable's value
    #   n             — execute the next line
    #   s             — step into a function call
    #   c             — continue to the next breakpoint
    #   w             — show the call stack
    # In an interview, mentioning "I'd set a breakpoint here" shows maturity.
    # Don't use breakpoint() in committed code — it's for local debugging only.
    #
    # PYTHONBREAKPOINT environment variable:
    #   export PYTHONBREAKPOINT=ipdb.set_trace   # use ipdb instead of pdb
    #   export PYTHONBREAKPOINT=0                # disable all breakpoint() calls
    # This is gold in CI: PYTHONBREAKPOINT=0 makes forgotten breakpoint() calls
    # into no-ops instead of hanging the build waiting for stdin.
    print("  TIP: For interactive debugging, use breakpoint() (Python 3.7+).")
    print("       PYTHONBREAKPOINT=0 disables them; =module.fn swaps the tool.\n")


# ---------------------------------------------------------------------------
# 4b. LOGGING EXCEPTIONS WITH FULL STACK TRACES
# ---------------------------------------------------------------------------
# When a production service catches an exception, you still want the stack
# trace in the logs.  Two idioms:
#
#   1. logger.exception("context")  — inside an except: block only.  Logs at
#      ERROR level AND appends the current traceback automatically.
#
#   2. logger.error("context", exc_info=True)  — same effect, more explicit.
#      Useful when the log level isn't ERROR (e.g., exc_info on WARNING).
#
# Don't do: logger.error(str(e))  — that throws away the stack trace.
#
# For one-off debugging (not logging), traceback.print_exc() dumps the
# traceback for the currently-handled exception to stderr.  Useful inside
# a script to see where a swallowed exception came from without stopping
# the program.


def case_study_logging_exceptions():
    """Show the right way to log an exception with its traceback."""
    import logging
    import io
    import traceback

    print("=" * 60)
    print("CASE STUDY: Logging exceptions")
    print("=" * 60)

    # Set up a logger that writes to an in-memory buffer so we can print it.
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("    %(levelname)s: %(message)s"))
    logger = logging.getLogger("demo.exc")
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    def risky():
        return {"a": 1}["missing"]

    try:
        risky()
    except KeyError:
        # PREFERRED: logger.exception — includes the traceback automatically.
        logger.exception("failed while looking up required key")

    print("  logger.exception output (traceback included):")
    for line in buffer.getvalue().rstrip("\n").split("\n"):
        print(line)
    print("  Without logger.exception, you'd see only the one-line message.\n")

    # traceback.print_exc() is handy when you want the traceback but don't
    # have a logger set up.  Great for debugging scripts.
    print("  traceback.print_exc() equivalent (captured to a string):")
    try:
        risky()
    except KeyError:
        trace = traceback.format_exc().rstrip()
        # Print only the last 3 lines for brevity in this demo.
        for line in trace.split("\n")[-3:]:
            print(f"    {line}")
    print()


# ============================================================================
# 5. ASSERT STATEMENTS AS DEVELOPMENT-TIME CHECKS
# ============================================================================
# assert statements are NOT for production error handling (use exceptions for
# that).  They're for catching "this should NEVER happen" situations during
# development.
#
# Think of them as executable documentation of your assumptions.

def case_study_assert_checks():
    """Show how asserts catch assumption violations early."""
    print("=" * 60)
    print("CASE STUDY: Assert as a development check")
    print("=" * 60)

    def apply_discount(price, discount_pct):
        # These asserts document and enforce preconditions.
        # If someone passes a negative price, we find out immediately
        # rather than silently producing nonsense downstream.
        assert price >= 0, f"Price must be non-negative, got {price}"
        assert 0 <= discount_pct <= 100, f"Discount must be 0-100, got {discount_pct}"

        result = price * (1 - discount_pct / 100)

        # Postcondition check: result should never exceed original price.
        assert result <= price, f"Discounted price {result} > original {price}"
        return round(result, 2)

    # Valid call
    print(f"  $80 with 25% off = ${apply_discount(80, 25)}")

    # This would trigger the assert (uncomment to see):
    #   apply_discount(80, 150)  → AssertionError: Discount must be 0-100, got 150
    print(f"  Asserts catch bad inputs before they cause silent wrong answers.")
    print(f"  NOTE: Don't use assert for user input validation in production —")
    print(f"  assert is disabled when Python runs with -O (optimize).\n")


# ============================================================================
# 6. BINARY SEARCH DEBUGGING
# ============================================================================
# When a long function produces wrong output and you can't spot the bug by
# reading, use a binary search approach:
#
#   1. Comment out the SECOND HALF of the function.  Return a dummy value
#      or print the intermediate state.
#   2. Is the intermediate state correct?  → Bug is in the second half.
#      Is it already wrong?               → Bug is in the first half.
#   3. Repeat on the identified half.
#
# This works in interviews too — you can say "Let me check whether the data
# is correct at this midpoint" and trace values mentally.

def case_study_binary_search_debugging():
    """A multi-step pipeline with a bug buried in the middle."""
    print("=" * 60)
    print("CASE STUDY: Binary search debugging")
    print("=" * 60)

    def process_scores(raw_scores):
        # Step 1: Filter out invalid scores
        valid = [s for s in raw_scores if isinstance(s, (int, float)) and s >= 0]

        # Step 2: Normalize to 0-100 scale (BUG WAS HERE)
        # Original buggy code: max_score = 100
        # The intent was to normalize relative to the actual max, not to 100.
        max_score = max(valid) if valid else 1
        normalized = [round(s / max_score * 100, 1) for s in valid]

        # Step 3: Assign letter grades
        def to_grade(n):
            if n >= 90: return "A"
            if n >= 80: return "B"
            if n >= 70: return "C"
            if n >= 60: return "D"
            return "F"

        return [(n, to_grade(n)) for n in normalized]

    raw = [45, 92, -1, "N/A", 78, 88]
    result = process_scores(raw)
    print(f"  Input:  {raw}")
    print(f"  Output: {result}")
    print(f"  Debugging approach: check `valid` after Step 1, then `normalized`")
    print(f"  after Step 2.  Whichever step first shows wrong data has the bug.\n")


# ============================================================================
# 7. OFF-BY-ONE ERRORS
# ============================================================================
# Off-by-one (OBO) errors are among the most common bugs.  They show up in:
#   - Loop boundaries (< vs <=)
#   - Slice endpoints (remember: end index is EXCLUSIVE)
#   - range() calls (range(n) gives 0..n-1, not 0..n)
#   - String/list indexing (first element is [0], last is [-1] or [len-1])

def case_study_off_by_one():
    """Three classic off-by-one scenarios."""
    print("=" * 60)
    print("CASE STUDY: Off-by-one errors")
    print("=" * 60)

    # --- Scenario A: Fence-post error ---
    # "How many fence posts do you need for a 10-section fence?"
    # Answer: 11 posts.  Getting this wrong is a classic OBO.
    def count_segments(points):
        # BUG pattern: returning len(points) instead of len(points) - 1
        # for number of segments between points.
        segments = len(points) - 1  # 4 points → 3 segments
        return max(segments, 0)

    points = [0, 10, 20, 30]
    print(f"  Fence-post: {len(points)} points → {count_segments(points)} segments")

    # --- Scenario B: range() boundary ---
    # Task: print numbers 1 through 5.
    buggy_range = list(range(1, 5))    # [1, 2, 3, 4]  — MISSING 5!
    fixed_range = list(range(1, 6))    # [1, 2, 3, 4, 5]
    print(f"  range(1, 5) = {buggy_range}  ← missing 5!")
    print(f"  range(1, 6) = {fixed_range}  ← correct")

    # --- Scenario C: Slice endpoints ---
    # Slices are [start, end) — the end index is EXCLUSIVE.
    text = "Hello, World!"
    buggy_slice = text[0:5]    # "Hello" — correct
    # But if you wanted "World": text[7:12], NOT text[7:11]
    print(f"  text[7:12] = '{text[7:12]}'  ← correct")
    print(f"  text[7:11] = '{text[7:11]}'  ← off by one, missing 'd'")

    # INTERVIEW TIP: When you see a loop or slice boundary, always check
    # the FIRST and LAST iteration/element.  Those are where OBOs hide.
    print()


# ============================================================================
# 8. THE "IT WORKS SOMETIMES" CHECKLIST
# ============================================================================
# Intermittent bugs are the hardest.  When a test passes sometimes and fails
# other times, check this list:
#
#   1. MUTABLE DEFAULT ARGUMENTS
#   2. DICT/SET ORDERING ASSUMPTIONS
#   3. FLOATING-POINT COMPARISON
#   4. SHARED MUTABLE STATE BETWEEN TESTS

def case_study_intermittent_bugs():
    """Four classic sources of 'it works sometimes' bugs."""
    print("=" * 60)
    print("CASE STUDY: The 'it works sometimes' checklist")
    print("=" * 60)

    # --- 1. Mutable default arguments ---
    # This is Python's most famous gotcha.
    def append_to_buggy(item, lst=[]):
        # The default [] is created ONCE when the function is defined,
        # then REUSED across every call.  Each call mutates the SAME list.
        lst.append(item)
        return lst

    def append_to_fixed(item, lst=None):
        if lst is None:
            lst = []   # Fresh list each time
        lst.append(item)
        return lst

    # Buggy version accumulates across calls:
    r1 = append_to_buggy("a")
    r2 = append_to_buggy("b")
    print(f"  Mutable default bug: call1={r1}, call2={r2}")
    # r1 and r2 are BOTH ['a', 'b'] because they share the same list!

    # Fixed version:
    r3 = append_to_fixed("a")
    r4 = append_to_fixed("b")
    print(f"  Mutable default fix: call1={r3}, call2={r4}")

    # --- 2. Ordering assumptions ---
    # Before Python 3.7, dicts didn't guarantee insertion order.
    # Sets STILL don't.  If your test checks order, it may be fragile.
    s = {3, 1, 2}
    # list(s) might be [1, 2, 3] or [3, 1, 2] — don't depend on it.
    print(f"  Set ordering: set={{3,1,2}} → list = {list(s)}  (order not guaranteed)")

    # --- 3. Floating-point comparison ---
    a = 0.1 + 0.2
    b = 0.3
    print(f"  Float comparison: 0.1 + 0.2 == 0.3? → {a == b}")
    print(f"    0.1 + 0.2 is actually {a!r}")
    print(f"    Fix: use math.isclose(a, b) or assertAlmostEqual in tests")

    # --- 4. Shared mutable state between tests ---
    # This one is demonstrated in 03_unittest_fundamentals.py.
    # If tests share a class-level list and mutate it, the outcome depends
    # on execution order — which unittest does NOT guarantee.
    print(f"  Shared state: if tests mutate a class-level list, order matters.")
    print(f"    Fix: create fresh state in setUp(), never mutate shared fixtures.\n")


# ============================================================================
# CASE STUDY: Mutating a collection while iterating over it
# ============================================================================
# This is one of the most common Python bugs and appears in two forms:
#
#   1. LISTS: silently skips elements (no error, just wrong results)
#   2. DICTS: raises RuntimeError in Python 3
#
# Both are hard to spot because the code LOOKS correct.

def case_study_mutation_while_iterating():
    """Demonstrate the list-skip and dict-RuntimeError patterns."""
    print("=" * 60)
    print("CASE STUDY: Mutating a collection while iterating")
    print("=" * 60)

    # --- 1. Lists: silent element skipping ---
    # Scenario: remove all completed tasks from a list.
    tasks = ["done", "done", "pending", "done", "pending"]

    # BUGGY: removing items shifts indices, so the loop skips elements.
    buggy_tasks = list(tasks)  # copy so we can compare
    for task in buggy_tasks:
        if task == "done":
            buggy_tasks.remove(task)

    print(f"  Original:  {tasks}")
    print(f"  After buggy removal: {buggy_tasks}")
    # Expected: ["pending", "pending"]
    # Actual:   ["done", "pending", "pending"] — second "done" was skipped!
    # Why: after removing index 0, "done" at index 1 shifts to index 0,
    # but the iterator moves to index 1, skipping it.

    # FIX 1: Build a new list with a comprehension (preferred).
    fixed_1 = [t for t in tasks if t != "done"]
    print(f"  Fix 1 (comprehension): {fixed_1}")

    # FIX 2: Iterate over a copy of the list.
    # CAVEAT: .remove() deletes the first match by VALUE, not by position.
    # This works here because all "done" values are interchangeable. If your
    # list has duplicates you need to keep, use Fix 1 or Fix 3 instead.
    fixed_2 = list(tasks)
    for task in list(fixed_2):   # list() makes a copy to iterate
        if task == "done":
            fixed_2.remove(task)
    print(f"  Fix 2 (copy + remove): {fixed_2}")

    # FIX 3: Iterate in reverse (safe because removals don't shift earlier indices).
    fixed_3 = list(tasks)
    for i in range(len(fixed_3) - 1, -1, -1):
        if fixed_3[i] == "done":
            del fixed_3[i]
    print(f"  Fix 3 (reverse iteration): {fixed_3}")

    # --- 2. Dicts: RuntimeError ---
    # Scenario: remove expired entries from a cache dict.
    cache = {"a": 1, "b": 2, "c": 3, "d": 4}

    # BUGGY: deleting keys while iterating raises RuntimeError in Python 3.
    print(f"\n  Dict before cleanup: {cache}")
    try:
        for key in cache:
            if cache[key] % 2 == 0:
                del cache[key]
    except RuntimeError as e:
        print(f"  RuntimeError: {e}")
        # "dictionary changed size during iteration"

    # FIX: iterate over a snapshot of the keys.
    cache = {"a": 1, "b": 2, "c": 3, "d": 4}  # reset
    for key in list(cache.keys()):  # list() takes a snapshot
        if cache[key] % 2 == 0:
            del cache[key]
    print(f"  Dict after safe cleanup: {cache}")  # {'a': 1, 'c': 3}

    # Or use a dict comprehension:
    cache = {"a": 1, "b": 2, "c": 3, "d": 4}
    cache = {k: v for k, v in cache.items() if v % 2 != 0}
    print(f"  Dict comprehension cleanup: {cache}")  # {'a': 1, 'c': 3}

    print()
    print("  KEY RULE: never add/remove elements to a collection you are")
    print("  currently iterating over.  Build a new collection, or iterate")
    print("  over a copy (list(d.keys()), list(items), reversed range).\n")


# ============================================================================
# MAIN — Run all case studies
# ============================================================================

def main():
    print()
    print("Guide 04 — Debugging Strategies")
    print("Each section below walks through a common debugging scenario.\n")

    case_study_traceback()
    case_study_common_errors()
    case_study_print_debugging()
    case_study_logging_exceptions()
    case_study_assert_checks()
    case_study_binary_search_debugging()
    case_study_off_by_one()
    case_study_intermittent_bugs()
    case_study_mutation_while_iterating()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Follow the workflow: reproduce → isolate → diagnose → fix → verify")
    print("  2. Read tracebacks bottom-to-top")
    print("  3. Use labeled print() at midpoints to narrow the search space")
    print("  4. Check boundaries first for off-by-one errors")
    print("  5. For intermittent bugs: check mutable defaults, ordering, floats")
    print("  6. Never mutate a collection while iterating — build a new one")
    print()


if __name__ == "__main__":
    main()
