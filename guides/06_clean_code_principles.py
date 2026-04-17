"""
Guide 06: Clean Code Principles
================================
Paired "before / after" examples of common code smells and refactorings.
Run:  python guides/06_clean_code_principles.py
"""

# Nothing imported from typing — in Python 3.10+ we use the pipe syntax
# (`X | None`, `X | Y`) and lowercase builtins (`list[str]`, `dict[str, int]`)
# natively. typing.Optional / typing.Union are legacy.

# ---
# Section 1: Naming -- descriptive names over abbreviations
# ---
# BEFORE: cryptic names force the reader to decode intent.

def calc(d, r):
    """What does this do?  Nobody knows without reading every line."""
    t = 0
    for i in d:
        t += i["a"] * (1 - r)
    return t


# AFTER: the function name, parameter names, and local variables all
# communicate intent.  A newcomer can understand this without comments.

def calculate_discounted_total(items, discount_rate):
    """Return the total price of *items* after applying *discount_rate*
    (0.0 to 1.0) to each item's amount."""
    total = 0
    for item in items:
        total += item["amount"] * (1 - discount_rate)
    return total


def demo_naming():
    print("=" * 60)
    print("SECTION 1: Descriptive naming")
    print("=" * 60)
    items = [{"amount": 100}, {"amount": 50}]
    # The "before" version uses cryptic key "a" for amount.
    cryptic_items = [{"a": 100}, {"a": 50}]

    # Both produce the same result, but one is readable.
    assert calc(cryptic_items, 0.1) == calculate_discounted_total(items, 0.1)
    print("  BEFORE: calc(d, r) -- caller has no idea what d and r mean")
    print("  AFTER:  calculate_discounted_total(items, discount_rate)")
    print("  Same result, dramatically clearer intent\n")


# ---
# Section 2: Function length and single responsibility
# ---
# BEFORE: one function does validation, transformation, AND persistence.
_saved_users = []  # pretend database

def handle_signup_before(name, email, age):
    if not name or len(name) < 2:           # validation
        return {"error": "bad name"}
    if "@" not in email:
        return {"error": "bad email"}
    if age < 13:
        return {"error": "too young"}
    clean_name = name.strip().title()       # transformation
    clean_email = email.strip().lower()
    user = {"name": clean_name, "email": clean_email, "age": age}
    _saved_users.append(user)               # persistence
    return user

# AFTER: each concern lives in its own function.

def validate_signup(name, email, age):
    """Return an error string or None if inputs are valid."""
    if not name or len(name) < 2:
        return "bad name"
    if "@" not in email:
        return "bad email"
    if age < 13:
        return "too young"
    return None

def normalize_user(name, email, age):
    """Return a cleaned-up user dict."""
    return {"name": name.strip().title(), "email": email.strip().lower(), "age": age}

def save_user(user):
    """Persist a user dict (stub)."""
    _saved_users.append(user)

def handle_signup_after(name, email, age):
    """Orchestrate signup: validate, normalize, save."""
    error = validate_signup(name, email, age)
    if error:
        return {"error": error}
    user = normalize_user(name, email, age)
    save_user(user)
    return user


def demo_single_responsibility():
    print("=" * 60)
    print("SECTION 2: Single responsibility")
    print("=" * 60)
    result = handle_signup_after("  ada  ", "ADA@Example.COM", 30)
    assert result == {"name": "Ada", "email": "ada@example.com", "age": 30}
    # Now we can unit-test validate_signup and normalize_user in isolation.
    assert validate_signup("", "x@y", 20) == "bad name"
    assert normalize_user("  BOB  ", "BOB@X.COM", 25)["email"] == "bob@x.com"
    print("  Each sub-function is testable in isolation")
    print("  The orchestrator is a simple 4-line pipeline\n")


# ---
# Section 3: DRY vs. WET -- when duplication is OK
# ---
# DRY (Don't Repeat Yourself) is good, but premature abstraction is worse.
# WET = "Write Everything Twice" -- wait until you see THREE duplications
# before extracting a shared helper.

def demo_dry_wet():
    print("=" * 60)
    print("SECTION 3: DRY vs. WET")
    print("=" * 60)
    print("""  BEFORE (over-abstracted):
    def make_query(table, filters, joins, order, group, having):
        ...  # 80-line generic query builder used in only 2 places

  AFTER (acceptable duplication):
    def get_active_users():  return db.query("SELECT ... WHERE active")
    def get_recent_orders(): return db.query("SELECT ... WHERE date > X")

  These queries look similar but evolve independently.  Forcing them
  through a shared abstraction couples them unnecessarily.

  RULE OF THUMB:
    - 2 occurrences: tolerate it.  3 occurrences: extract a helper.
    - Ask: "Do these change for the SAME reason?"
      If not, it is not real duplication -- it just looks alike.
""")


# ---
# Section 4: Guard clauses vs. deeply nested conditionals
# ---
# BEFORE: deep nesting ("arrow code").

def process_order_before(order):
    if order is not None:
        if order.get("items"):
            if order.get("customer_id"):
                total = sum(i["price"] for i in order["items"])
                if total > 0:
                    return {"customer": order["customer_id"], "total": total}
                else:
                    return {"error": "empty total"}
            else:
                return {"error": "no customer"}
        else:
            return {"error": "no items"}
    else:
        return {"error": "no order"}


# AFTER: guard clauses -- reject bad states early, then proceed with the
# happy path at the top indentation level.

def process_order_after(order):
    if order is None:
        return {"error": "no order"}
    if not order.get("items"):
        return {"error": "no items"}
    if not order.get("customer_id"):
        return {"error": "no customer"}

    total = sum(item["price"] for item in order["items"])
    if total <= 0:
        return {"error": "empty total"}

    return {"customer": order["customer_id"], "total": total}


def demo_guard_clauses():
    print("=" * 60)
    print("SECTION 4: Guard clauses vs. deep nesting")
    print("=" * 60)
    good_order = {"customer_id": "C1", "items": [{"price": 10}, {"price": 20}]}

    # Both versions produce identical results.
    assert process_order_before(good_order) == process_order_after(good_order)
    assert process_order_before(None) == process_order_after(None)
    assert process_order_before({}) == process_order_after({})

    print("  BEFORE: 4 levels of nesting to reach the happy path")
    print("  AFTER:  flat -- each guard returns early on failure\n")


# ---
# Section 5: Docstrings -- what to include, when they matter
# ---

# BAD docstring: restates the code without adding value.
def add(a, b):
    """Add a and b and return the result."""     # we can see that already!
    return a + b


# GOOD docstring: explains WHY, constraints, and edge cases.
def retry(func, max_attempts=3, backoff_factor=2.0):
    """Call *func* up to *max_attempts* times with exponential backoff.

    Args:
        func: A callable with no arguments; raises on failure.
        max_attempts: Total tries before giving up (default 3).
        backoff_factor: Multiplier for wait time between retries.

    Returns:
        The return value of *func* on the first successful call.

    Raises:
        The exception from the final failed attempt.
    """
    last_exc = None
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
    raise last_exc


def demo_docstrings():
    print("=" * 60)
    print("SECTION 5: Docstrings")
    print("=" * 60)
    print("  BAD:  'Add a and b and return the result.'  -- restates the code")
    print("  GOOD: explains args, returns, raises, and edge cases")
    print("  Write docstrings on public APIs; skip them on tiny helpers.\n")


# ---
# Section 6: Type hints as documentation
# ---

# WITHOUT type hints -- caller must read the body to know what to pass.
def find_longest(items):
    best = ""
    for item in items:
        if len(item) > len(best):
            best = item
    return best

# WITH type hints -- the signature IS documentation.
def find_longest_typed(items: list[str]) -> str:
    """Return the longest string in *items*, or '' if empty."""
    best = ""
    for item in items:
        if len(item) > len(best):
            best = item
    return best

# `dict | None` signals that None is a valid return value. In 3.10+ the pipe
# syntax is idiomatic; typing.Optional is legacy and should only appear if
# you're maintaining pre-3.10 code.
def lookup_user(user_id: int) -> dict | None:
    """Return user dict or None if not found."""
    users = {1: {"name": "Ada"}, 2: {"name": "Grace"}}
    return users.get(user_id)


def demo_type_hints():
    print("=" * 60)
    print("SECTION 6: Type hints as documentation")
    print("=" * 60)
    assert find_longest_typed(["a", "bb", "ccc"]) == "ccc"
    assert lookup_user(99) is None
    print("  find_longest_typed(items: list[str]) -> str")
    print("  lookup_user(user_id: int) -> dict | None")
    print("  The signature tells you what to pass and what to expect.\n")


# ---
# Section 7: Code smells
# ---

# SMELL 1: Long parameter lists.
# BEFORE: eight positional arguments that callers have to get in the right order.
def create_report_before(title, author, dept, start, end, fmt, lang, debug):
    pass  # imagine 50 lines here


# AFTER: group related parameters into a dataclass.  @dataclass gives you
# __init__, __repr__, __eq__ and type-checked field names for free.  Callers
# use keyword-style construction, which reads like a named-argument call.
from dataclasses import dataclass


@dataclass
class ReportConfig:
    title: str
    author: str
    department: str
    start_date: str
    end_date: str
    format: str = "pdf"
    language: str = "en"
    debug: bool = False


def create_report_after(config: ReportConfig) -> None:
    """Generate a report described by *config*."""
    _ = config  # imagine 50 lines here
    return None


# SMELL 2: Boolean flag that splits a function into two behaviors.
# BEFORE:
def send_message_before(recipient, body, is_urgent):
    if is_urgent:
        pass   # completely different code path: pager, escalation
    else:
        pass   # normal email path

# AFTER: two functions with clear names.
def send_message(recipient: str, body: str):
    """Send a normal message."""
    pass

def send_urgent_alert(recipient: str, body: str):
    """Send an urgent message via pager with escalation."""
    pass

# SMELL 3: Catch-all exception handling.
# BEFORE:
def load_config_before(path):
    try:
        with open(path) as f:
            return f.read()
    except Exception:        # catches KeyboardInterrupt, SystemExit, ...
        return "default"

# AFTER: catch only the exceptions you expect.
def load_config_after(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return "default"
    except PermissionError:
        raise  # let the caller know about permission problems


def demo_code_smells():
    print("=" * 60)
    print("SECTION 7: Code smells")
    print("=" * 60)
    print("""  SMELL 1 -- Long parameter lists:
    BEFORE: create_report(title, author, dept, start, end, fmt, lang, debug)
    AFTER:  create_report(ReportConfig(title=..., author=...))  -- named, typed

  SMELL 2 -- Boolean flag that changes behavior:
    BEFORE: send_message(to, body, is_urgent=True)
    AFTER:  send_message(to, body)  /  send_urgent_alert(to, body)
    If a flag creates TWO code paths, make TWO functions.

  SMELL 3 -- Catch-all exceptions:
    BEFORE: except Exception: return "default"
    AFTER:  except FileNotFoundError: return "default"
    Catch only what you expect; let the rest propagate.
""")
    # Quick runtime check on load_config_after.
    assert load_config_after("/nonexistent/path/config.txt") == "default"
    print("  PASS: load_config_after returns default for missing file\n")


# ---
# Run all demos
# ---

def main():
    print()
    print("GUIDE 06: Clean Code Principles")
    print("=" * 60)
    print()
    demo_naming()
    demo_single_responsibility()
    demo_dry_wet()
    demo_guard_clauses()
    demo_docstrings()
    demo_type_hints()
    demo_code_smells()
    print("All sections passed.")


if __name__ == "__main__":
    main()
