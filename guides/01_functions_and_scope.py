"""
Guide 01: Functions and Scope
=============================
Run this file:  python guides/01_functions_and_scope.py

This guide covers core function behavior and scoping rules that come up
frequently in Python interviews. Every section is runnable and prints its
own output so you can follow along.
"""

# ---------------------------------------------------------------------------
# 1. FUNCTION DEFINITION AND ARGUMENT TYPES
# ---------------------------------------------------------------------------
# Python supports several ways to pass arguments to a function.
# Understanding the order and rules is essential for interviews.

# Positional and keyword arguments
def greet(name, greeting="Hello"):
    # 'name' is a required positional argument.
    # 'greeting' is an optional keyword argument with a default value.
    return f"{greeting}, {name}!"

print("=== 1. Argument Types ===")
print(greet("Alice"))                # positional only
print(greet("Bob", greeting="Hi"))   # keyword argument overrides default
print(greet("Carol", "Hey"))         # positional for both -- this works too
print()

# *args collects extra positional arguments into a tuple.
# **kwargs collects extra keyword arguments into a dict.
def show_args(required, *args, **kwargs):
    print(f"  required: {required}")
    print(f"  args:     {args}")       # tuple of extra positionals
    print(f"  kwargs:   {kwargs}")     # dict of extra keywords

print("Calling show_args(1, 2, 3, x=10, y=20):")
show_args(1, 2, 3, x=10, y=20)
print()

# Keyword-only arguments: anything after * (or *args) must be passed by name.
def keyword_only_example(a, b, *, verbose=False):
    if verbose:
        print(f"  a={a}, b={b}")

print("Keyword-only parameter 'verbose' must be named:")
keyword_only_example(1, 2, verbose=True)
# keyword_only_example(1, 2, True)  # <-- would raise TypeError
print()


# ---------------------------------------------------------------------------
# 2. THE MUTABLE DEFAULT ARGUMENT TRAP
# ---------------------------------------------------------------------------
# One of the most common Python interview questions.
# Default argument values are evaluated ONCE -- at function definition time,
# not each time the function is called. If the default is mutable (like a
# list or dict), the same object is reused across calls.

def append_to(item, target=[]):          # <-- dangerous default!
    target.append(item)
    return target

print("=== 2. Mutable Default Argument Trap ===")

# CHALLENGE: What do these three calls print?
# Think about it before scrolling down...
result1 = append_to(1)
print(f"  Call 1: {result1}")

result2 = append_to(2)
print(f"  Call 2: {result2}")      # Did you expect [2]?

result3 = append_to(3)
print(f"  Call 3: {result3}")      # All three share the SAME list!

# ANSWER: Call 1 prints [1], Call 2 prints [1, 2], Call 3 prints [1, 2, 3].
# The list object is created once and kept as an attribute of the function.
print(f"  Proof -- they're the same object: {result1 is result2}")  # True

# The fix: use None as a sentinel and create a new list inside the function.
def append_to_fixed(item, target=None):
    if target is None:
        target = []                      # fresh list on every call
    target.append(item)
    return target

print(f"  Fixed call 1: {append_to_fixed(1)}")   # [1]
print(f"  Fixed call 2: {append_to_fixed(2)}")   # [2] -- independent!
print()


# ---------------------------------------------------------------------------
# 3. VARIABLE SCOPE: THE LEGB RULE
# ---------------------------------------------------------------------------
# Python resolves names in this order:
#   L - Local:     inside the current function
#   E - Enclosing: inside any enclosing (outer) function (closures)
#   G - Global:    at the module level
#   B - Built-in:  Python's built-in names (len, print, etc.)

x = "global x"

def outer():
    x = "enclosing x"            # E -- enclosing scope for inner()

    def inner():
        x = "local x"            # L -- local scope
        print(f"  inner sees: {x}")

    def inner_no_local():
        # No local x here, so Python checks the enclosing scope.
        print(f"  inner_no_local sees: {x}")

    inner()
    inner_no_local()

print("=== 3. LEGB Scope Rule ===")
outer()
print(f"  module level sees: {x}")   # global x is untouched
print()

# The 'global' and 'nonlocal' keywords let you write to outer scopes.
counter = 0

def increment():
    global counter               # without this, assigning counter would
    counter += 1                 # create a local variable and fail

def outer_counter():
    count = 0
    def inc():
        nonlocal count           # refers to enclosing scope's 'count'
        count += 1
    inc()
    inc()
    print(f"  nonlocal count after 2 increments: {count}")

print("global / nonlocal keywords:")
increment()
increment()
print(f"  global counter after 2 increments: {counter}")
outer_counter()
print()


# ---------------------------------------------------------------------------
# 4. CLOSURES AND LATE BINDING (LOOP VARIABLE CAPTURE)
# ---------------------------------------------------------------------------
# A closure is a function that remembers the environment in which it was
# created. This is powerful but leads to a classic gotcha with loops.

print("=== 4. Closures and Late Binding ===")

def make_multiplier(n):
    # 'n' is captured by the inner function -- this is a closure.
    def multiplier(x):
        return x * n
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)
print(f"  double(5) = {double(5)}")   # 10
print(f"  triple(5) = {triple(5)}")   # 15

# GOTCHA: Late binding in loops.
# The closure captures the VARIABLE, not its VALUE at creation time.
# By the time the function is called, the loop variable has its final value.

functions = []
for i in range(4):
    functions.append(lambda: i)     # all lambdas share the same 'i'

# CHALLENGE: What does this print?
print(f"  Late binding: {[f() for f in functions]}")
# ANSWER: [3, 3, 3, 3] -- every lambda sees i=3 (the final loop value).

# Fix 1: Use a default argument to capture the current value.
functions_fixed = []
for i in range(4):
    functions_fixed.append(lambda i=i: i)  # default arg evaluated NOW

print(f"  Fixed:        {[f() for f in functions_fixed]}")  # [0, 1, 2, 3]

# Fix 2: Use a factory function (same idea as make_multiplier above).
def make_const(val):
    return lambda: val

functions_fixed2 = [make_const(i) for i in range(4)]
print(f"  Fixed (v2):   {[f() for f in functions_fixed2]}")  # [0, 1, 2, 3]
print()


# ---------------------------------------------------------------------------
# 5. RETURN VALUES VS. IN-PLACE MUTATION
# ---------------------------------------------------------------------------
# Many built-in methods MUTATE the object and return None.
# This trips people up in interviews when they assign the result.

print("=== 5. Return Values vs. In-Place Mutation ===")

nums = [3, 1, 2]
result = nums.sort()      # .sort() sorts IN PLACE and returns None
print(f"  nums.sort() returned: {result}")   # None
print(f"  nums is now: {nums}")              # [1, 2, 3]

# If you want a NEW sorted list, use the built-in sorted() function.
original = [3, 1, 2]
new_sorted = sorted(original)
print(f"  sorted() returned: {new_sorted}")  # [1, 2, 3]
print(f"  original unchanged: {original}")   # [3, 1, 2]

# Same pattern applies to: list.append(), list.extend(), list.reverse(),
# dict.update(), set.add(), etc. -- they all return None.

# CHALLENGE: What does this print?
my_list = [4, 2, 7]
chained = my_list.append(5)
print(f"  chained = my_list.append(5) -> chained is {chained}")
# ANSWER: None. The append happened, but the return value is None.
print(f"  my_list is now: {my_list}")  # [4, 2, 7, 5]
print()


# ---------------------------------------------------------------------------
# 6. FIRST-CLASS FUNCTIONS
# ---------------------------------------------------------------------------
# In Python, functions are objects. You can assign them to variables, store
# them in data structures, and pass them as arguments to other functions.

print("=== 6. First-Class Functions ===")

def shout(text):
    return text.upper()

def whisper(text):
    return text.lower()

# Passing a function as an argument
def apply_and_print(func, text):
    print(f"  {func.__name__}('{text}') -> '{func(text)}'")

apply_and_print(shout, "hello")
apply_and_print(whisper, "HELLO")

# Storing functions in a data structure
operations = {"loud": shout, "quiet": whisper}
for name, fn in operations.items():
    print(f"  operations['{name}']('test') -> '{fn('test')}'")

# Using built-in higher-order functions: map, filter, sorted with key
words = ["banana", "apple", "cherry"]
print(f"  sorted by length: {sorted(words, key=len)}")
print(f"  uppercased:       {list(map(str.upper, words))}")
print(f"  len > 5:          {list(filter(lambda w: len(w) > 5, words))}")
print()


# ---------------------------------------------------------------------------
# 7. GENERATORS AND ITERATOR CONSUMPTION
# ---------------------------------------------------------------------------
# A generator is a function that uses `yield` instead of `return`.  Each call
# to next() runs the function until the next yield, then pauses.
#
# KEY GOTCHA: a generator (or any iterator) can only be consumed ONCE.
# After you've iterated through it, it's exhausted — iterating again yields
# nothing.  This is a common source of silent bugs.

print("=== 7. Generators and Iterator Consumption ===")


# --- 7a: Basic generator ---
def count_up_to(n):
    """Yield integers from 1 to n."""
    i = 1
    while i <= n:
        yield i
        i += 1


# Generators are lazy — nothing runs until you iterate.
gen = count_up_to(3)
print(f"  Generator object: {gen}")  # <generator object ...>
print(f"  next(gen) = {next(gen)}")  # 1
print(f"  next(gen) = {next(gen)}")  # 2
print(f"  list(gen) = {list(gen)}")  # [3]  (only the remaining item!)
print(f"  list(gen) = {list(gen)}")  # []   (exhausted — nothing left)


# --- 7b: The single-consumption trap ---
# Generator expressions look like list comprehensions but use ().
# They are also single-use.
def buggy_stats(numbers):
    """Attempt to compute both sum and count from a generator."""
    evens = (n for n in numbers if n % 2 == 0)
    total = sum(evens)       # consumes the generator
    count = sum(1 for _ in evens)  # generator is exhausted — always 0!
    return total, count


result = buggy_stats([1, 2, 3, 4, 5, 6])
print(f"\n  Buggy stats: total={result[0]}, count={result[1]}")
# Output: total=12, count=0  — count is wrong!

# FIX: materialize the generator into a list first, or use it once.
def fixed_stats(numbers):
    evens = [n for n in numbers if n % 2 == 0]  # list, not generator
    total = sum(evens)
    count = len(evens)
    return total, count


result = fixed_stats([1, 2, 3, 4, 5, 6])
print(f"  Fixed stats: total={result[0]}, count={result[1]}")
# Output: total=12, count=3


# --- 7c: Generator vs list — when to use each ---
# Use a GENERATOR when:
#   - The data is large and you only need one pass (saves memory).
#   - You're piping data through a chain of transformations.
# Use a LIST when:
#   - You need to iterate multiple times.
#   - You need len(), indexing, or slicing.
#   - The data fits comfortably in memory.
print()
print("  Rule of thumb: if you need the data more than once, use a list.")
print("  If you only need one pass, a generator saves memory.")
print()


# ---------------------------------------------------------------------------
# SUMMARY OF INTERVIEW TAKEAWAYS
# ---------------------------------------------------------------------------
# - Know the argument order: positional, *args, keyword-only, **kwargs.
# - Never use a mutable default argument; use None as a sentinel.
# - LEGB is the name lookup order. Use 'global' and 'nonlocal' to write
#   to outer scopes (but prefer returning values instead).
# - Closures capture variables by reference, not by value -- beware loops.
# - Methods like .sort(), .append(), .reverse() return None.
# - Functions are first-class objects: pass them around freely.
# - Generators yield values lazily and can only be consumed ONCE.

print("=== All sections complete. ===")
