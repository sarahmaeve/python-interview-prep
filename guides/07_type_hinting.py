"""
Guide 07: Type Hinting
======================
Run this file:  python guides/07_type_hinting.py

Type hints annotate the expected types of variables, parameters, and return
values.  They are optional at runtime but invaluable for:
  - Readability:    understand a function signature without reading the body.
  - IDE support:    autocompletion, inline warnings, refactoring tools.
  - Bug detection:  static checkers (mypy, pyright) catch bugs before runtime.
  - Documentation:  lives in code, enforced by tooling, never goes stale.

Interview angle: you will be expected to READ typed code quickly and spot
when a type annotation reveals a bug.
"""

# This guide targets Python 3.11+.  That means we can use the pipe union
# syntax (`int | None`), lowercase generics (`list[str]`, `dict[str, int]`),
# `typing.Self`, `typing.Required/NotRequired`, and `typing.assert_never`
# natively — no `from __future__ import annotations` required.

# Callable lives in collections.abc at runtime (3.9+); typing re-exports it
# for backward compatibility.  Prefer the collections.abc home.
from collections.abc import Callable
from typing import (
    Any,
    NotRequired,
    Protocol,
    Self,
    TypedDict,
    assert_never,
    runtime_checkable,
)

# ===========================================================================
# 1. BASIC TYPE ANNOTATIONS
# ===========================================================================
# Annotate variables, parameters, and return types.

# Variable annotations (Python 3.6+)
name: str = "Alice"
age: int = 30
balance: float = 99.95
active: bool = True

# Function annotations: param types after colon, return type after "->".

def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b

def greet(person: str, loud: bool = False) -> str:
    """Return a greeting string.  If *loud*, uppercase it."""
    msg = f"Hello, {person}!"
    return msg.upper() if loud else msg

# Functions that return nothing should be annotated -> None.
def log_message(msg: str) -> None:
    """Side-effect only: prints *msg* to stdout."""
    print(f"  [LOG] {msg}")

print("=" * 60)
print("SECTION 1: Basic type annotations")
print("=" * 60)
print(f"  add(3, 7)          = {add(3, 7)}")
print(f"  greet('Bob')       = {greet('Bob')}")
print(f"  greet('Bob', True) = {greet('Bob', True)}")
log_message("Type hints do NOT enforce types at runtime.")

# CHALLENGE: add("hello", "world") -- Python returns "helloworld" (concat).
# But mypy flags: incompatible type "str"; expected "int".
print(f"  add('hello', 'world') = {add('hello', 'world')}  # runs fine!")
print()

# ===========================================================================
# 2. COLLECTION TYPES
# ===========================================================================
# Python 3.9+: use lowercase builtins -- list[str], dict[str, int], etc.
# Before 3.9: from typing import List, Dict, Tuple, Set  (still common)

# Modern (3.9+) style -- preferred in new code
names: list[str] = ["Alice", "Bob", "Carol"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
coordinates: tuple[float, float] = (3.14, 2.72)
unique_ids: set[int] = {1, 2, 3}

# Variable-length tuples use an ellipsis:
#   tuple[int, ...]  means "a tuple of any number of ints"
all_scores: tuple[int, ...] = (95, 87, 72, 100)

def average(values: list[float]) -> float:
    """Return the arithmetic mean of *values*."""
    return sum(values) / len(values)

def word_count(text: str) -> dict[str, int]:
    """Return a mapping of word -> occurrence count."""
    counts: dict[str, int] = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts

print("=" * 60)
print("SECTION 2: Collection types")
print("=" * 60)
print(f"  names       : list[str]           = {names}")
print(f"  scores      : dict[str, int]      = {scores}")
print(f"  coordinates : tuple[float, float] = {coordinates}")
print(f"  average([1,2,3,4]) = {average([1, 2, 3, 4])}")
print()

# ===========================================================================
# 3. UNIONS AND OPTIONAL VALUES (PIPE SYNTAX)
# ===========================================================================
# In Python 3.10+, the pipe operator `|` is the idiomatic way to express
# union types:
#     X | None   (instead of Optional[X])
#     X | Y      (instead of Union[X, Y])
# typing.Optional and typing.Union still work but are legacy — prefer pipes
# in new code.

_USERS = {1: "Alice", 2: "Bob"}

def find_user(user_id: int) -> str | None:
    """Look up a user by ID.  Returns None if not found."""
    return _USERS.get(user_id)

# `X | Y` for "either type" when None is not involved.
def format_id(identifier: int | str) -> str:
    """Accept an int or string ID, return a normalized string form."""
    if isinstance(identifier, int):
        return f"ID-{identifier:05d}"
    return f"ID-{identifier.upper()}"

print("=" * 60)
print("SECTION 3: Optional and Union")
print("=" * 60)
print(f"  find_user(1)    = {find_user(1)!r}")
print(f"  find_user(999)  = {find_user(999)!r}  # None -- user not found")
print(f"  format_id(42)   = {format_id(42)}")
print(f"  format_id('abc')= {format_id('abc')}")

# CHALLENGE: result = find_user(1); result.upper()  -- would mypy catch it?
# YES -- "Item 'None' of 'Optional[str]' has no attribute 'upper'".
print("  ^ mypy would flag result.upper() without a None check")
print()

# ===========================================================================
# 4. TYPE ALIASES
# ===========================================================================
# Give complex annotations a name to improve readability.
# On 3.12+, `type UserMap = dict[int, str]` (PEP 695) is the recommended form —
# the `type` statement creates a lazy alias that plays well with forward
# references and tooling.  On 3.11 (this guide's floor) plain assignment still
# works and is widely used.

UserId = int
Username = str
UserMap = dict[UserId, Username]          # 3.11-compatible form

# On 3.12+ prefer:
#   type UserMap = dict[int, str]
#   type Matrix  = list[list[float]]

Matrix = list[list[float]]

def transpose(matrix: Matrix) -> Matrix:
    """Return the transpose of a 2-D matrix."""
    if not matrix:
        return []
    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]

print("=" * 60)
print("SECTION 4: Type aliases")
print("=" * 60)
m: Matrix = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
print(f"  Original matrix : {m}")
print(f"  Transposed      : {transpose(m)}")

user_db: UserMap = {1: "Alice", 2: "Bob"}
print(f"  user_db (UserMap): {user_db}")
print("  Aliases make complex types self-documenting.")
print()

# ===========================================================================
# 5. CALLABLE AND FUNCTION TYPES
# ===========================================================================
# Callable[[ArgType1, ArgType2], ReturnType] describes a function's shape.

def apply_twice(func: Callable[[int], int], value: int) -> int:
    """Apply *func* to *value* twice and return the result."""
    return func(func(value))

def double(n: int) -> int:
    return n * 2

def increment(n: int) -> int:
    return n + 1

# Callable[..., Any] means "any function" -- useful but less precise.
def with_logging(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap *func* to print before and after each call."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"    -> calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"    <- {func.__name__} returned {result!r}")
        return result
    return wrapper

print("=" * 60)
print("SECTION 5: Callable and function types")
print("=" * 60)
print(f"  apply_twice(double, 3)    = {apply_twice(double, 3)}")
print(f"  apply_twice(increment, 3) = {apply_twice(increment, 3)}")
logged_double = with_logging(double)
print("  Calling logged_double(5):")
logged_double(5)
print()

# ===========================================================================
# 6. TYPEDDICT
# ===========================================================================
# TypedDict specifies which keys exist and each value's type.
# Much safer than dict[str, Any] -- perfect for JSON-like data.

class UserProfile(TypedDict):
    name: str
    age: int
    email: str
    # NotRequired (3.11+) lets individual keys be optional without making the
    # whole dict partial (total=False).  Required/NotRequired work per-key.
    phone: NotRequired[str]

# Checked by mypy at analysis time; at runtime it's just a normal dict.
def format_profile(profile: UserProfile) -> str:
    return f"{profile['name']} (age {profile['age']}, {profile['email']})"

# 'phone' is NotRequired — this dict is still a valid UserProfile.
alice: UserProfile = {"name": "Alice", "age": 30, "email": "alice@example.com"}

print("=" * 60)
print("SECTION 6: TypedDict")
print("=" * 60)
print(f"  format_profile(alice) = {format_profile(alice)}")

# CHALLENGE: Would mypy catch this?
#   bad: UserProfile = {"name": "Bob", "age": "thirty", "email": "b@b.com"}
# YES -- "str" is incompatible with expected type "int" for key "age".
#
# CHALLENGE: Would mypy catch this?
#   print(alice["phone"])
# YES -- TypedDict "UserProfile" has no key "phone".  KeyError prevention!
print("  TypedDict catches wrong value types AND missing/extra keys.")
print()

# ===========================================================================
# 7. PROTOCOLS (STRUCTURAL SUBTYPING)
# ===========================================================================
# Protocols define interfaces by structure, not inheritance.
# "Duck typing with type safety."

# @runtime_checkable lets isinstance(obj, Drawable) work at runtime.
# Without it, Protocols are static-only.  Use sparingly — runtime
# structural checks are slower and weaker than explicit type checks.
@runtime_checkable
class Drawable(Protocol):
    """Any object with a .draw() -> str method satisfies this Protocol."""
    def draw(self) -> str: ...

class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def draw(self) -> str:
        return f"Circle(r={self.radius})"

class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def draw(self) -> str:
        return f"Square(s={self.side})"

def render(shape: Drawable) -> None:
    print(f"    Rendering: {shape.draw()}")

print("=" * 60)
print("SECTION 7: Protocols (structural subtyping)")
print("=" * 60)
print("  Circle and Square satisfy Drawable without inheriting from it:")
render(Circle(5.0))
render(Square(3.0))

# CHALLENGE: Would mypy catch Triangle with draw() -> int (not str)?
# YES -- return type mismatch against Drawable.draw() -> str.
print("  Protocols catch structural mismatches at check time.")
print()

# ===========================================================================
# 7b. typing.Self AND EXHAUSTIVENESS WITH typing.assert_never (3.11+)
# ===========================================================================
# Self refers to "the current class" — perfect for fluent-builder return
# types that should work correctly in subclasses.

class QueryBuilder:
    def __init__(self) -> None:
        self._filters: list[str] = []

    def where(self, condition: str) -> Self:
        """Return Self so subclasses get their own class back, not QueryBuilder."""
        self._filters.append(condition)
        return self

    def build(self) -> str:
        return " AND ".join(self._filters) or "TRUE"


# assert_never catches missed branches at type-check time.  If you add a new
# variant to a Literal or Enum later, mypy will flag every assert_never() call
# that can now be reached.
Status = str  # in real code this would be a Literal or StrEnum


def next_step(status: Status) -> str:
    if status == "pending":
        return "process"
    if status == "done":
        return "archive"
    if status == "failed":
        return "retry"
    # Unreachable IF we've handled every case.  mypy will verify.
    # At runtime this raises AssertionError, which is a useful safety net.
    assert_never(status)  # type: ignore[arg-type]


print("=" * 60)
print("SECTION 7b: typing.Self and exhaustiveness via assert_never")
print("=" * 60)
q = QueryBuilder().where("age > 18").where("active = true")
print(f"  QueryBuilder().where(...).where(...).build()  = {q.build()!r}")
print("  Self-typed fluent APIs survive subclassing — mypy verifies it.")
print("  assert_never() + Literal/Enum catches missed cases at check time.\n")


# ===========================================================================
# 8. COMMON PITFALLS
# ===========================================================================
print("=" * 60)
print("SECTION 8: Common pitfalls")
print("=" * 60)

# --- Pitfall A: Mutable default arguments ---

def append_item_bad(item: int, items: list[int] = []) -> list[int]:
    """BAD: the default [] is shared across all calls."""
    items.append(item)
    return items

def append_item_good(item: int, items: list[int] | None = None) -> list[int]:
    """GOOD: create a new list each time if none is provided."""
    if items is None:
        items = []
    items.append(item)
    return items
# Note: `items: list[int] | None = None` is the modern idiom.  Pre-3.10 code
# used `items: Optional[List[int]] = None` — both mean the same thing.

print("  Pitfall A: Mutable default argument")
result1 = append_item_bad(1)
result2 = append_item_bad(2)
print(f"    BAD  - call 1: {result1},  call 2: {result2}")
print(f"    Same object?  {result1 is result2}")  # True -- they share the list!

result3 = append_item_good(1)
result4 = append_item_good(2)
print(f"    GOOD - call 1: {result3}, call 2: {result4}")
print(f"    Same object?  {result3 is result4}")  # False -- independent lists
print()

# --- Pitfall B: Forgetting to return (implicit None) ---
# Annotated -> str but one branch has no return -- Python returns None.

def classify_age(age: int) -> str:
    """Return 'child', 'teen', or 'adult'.  But there is a bug..."""
    if age < 13:
        return "child"
    elif age < 18:
        return "teen"
    # BUG: no return for age >= 18 -- Python returns None!
    # mypy error: Missing return statement

print("  Pitfall B: Implicit None return")
print(f"    classify_age(10) = {classify_age(10)!r}")
print(f"    classify_age(15) = {classify_age(15)!r}")
print(f"    classify_age(25) = {classify_age(25)!r}  # BUG: None!")
print("    mypy would flag: 'Missing return statement'")
print()

# --- Pitfall C: Overly broad types (Any / bare dict) ---
class Event(TypedDict):
    kind: str
    payload: str

def process_event_good(event: Event) -> None:
    """GOOD: TypedDict pins down the exact shape."""
    print(f"    Processing {event['kind']}: {event['payload']}")

print("  Pitfall C: Overly broad types")
print("    dict[str, Any] -> mypy can't help you.")
print("    TypedDict      -> mypy catches typos in key names.")
sample_event: Event = {"kind": "click", "payload": "/home"}
process_event_good(sample_event)
print()

# ===========================================================================
# 9. RUNNING A TYPE CHECKER (mypy)
# ===========================================================================
print("=" * 60)
print("SECTION 9: Running a type checker")
print("=" * 60)
# Install:  pip install mypy
# Run:      mypy yourfile.py
#
# Example:  def get_name(user_id: int) -> str:
#               return {1: "Alice"}.get(user_id)    # BUG!
#
# mypy says: Incompatible return value type (got "Optional[str]",
#            expected "str") -- because dict.get() can return None.
#
# Fix: change to -> str | None, or use names[user_id], or add a default.
# In interviews, knowing WHY mypy flags something is the key insight.
print("  Install: pip install mypy")
print("  Run:     mypy yourfile.py")

# Live demo: works at runtime, but mypy catches the bug.
def get_name(user_id: int) -> str:
    names = {1: "Alice", 2: "Bob"}
    return names.get(user_id)  # type: ignore[return-value]

print(f"  get_name(1) = {get_name(1)!r}  # works at runtime")
print(f"  get_name(9) = {get_name(9)!r}  # returns None, violates -> str")
print("  mypy would catch this.  Runtime does not.\n")

# ===========================================================================
# 10. INTERVIEW CHEAT SHEET
# ===========================================================================
print("=" * 60)
print("SECTION 10: Interview cheat sheet")
print("=" * 60)
# Quick reference table (Python 3.11+):
#   x: int                    variable annotation
#   def f(a: int) -> str:     parameter + return type
#   list[str]                 list of strings
#   dict[str, int]            str keys, int values
#   tuple[int, str]           fixed-length tuple
#   tuple[int, ...]           variable-length tuple of ints
#   str | None                "str or None" (preferred over Optional[str])
#   int | str                 "int or str"   (preferred over Union[int, str])
#   Callable[[int], str]      function (int) -> str  (from collections.abc)
#   TypedDict                 dict with known structure
#     NotRequired[T]            optional key inside a TypedDict (3.11+)
#   Protocol                  structural interface (duck typing)
#     @runtime_checkable        opt-in isinstance() support for Protocols
#   Self                      "this class" in method signatures (3.11+)
#   assert_never(x)           exhaustiveness check — mypy catches missed cases
#   type Alias = ...          lazy type alias (3.12+)
#   def f[T](x: T) -> T:      PEP 695 generic function syntax (3.12+)
print("  Key interview talking points:")
print("  - Type hints are NOT enforced at runtime.")
print("  - They help you READ code faster and catch bugs BEFORE running.")
print("  - Use `X | None` when None is valid -- forces callers to check.")
print("  - Prefer TypedDict over dict[str, Any] for structured data.")
print("  - Protocols enable duck typing with static verification.")
print("  - Always run mypy/pyright in CI to keep hints honest.")

print("=" * 60)
print("Guide 07 complete. Try: mypy guides/07_type_hinting.py")
print("=" * 60)
