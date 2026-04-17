"""
Guide 09 — Modern Data Types: dataclass, StrEnum, Decimal
==========================================================
Run:  python guides/09_modern_data_types.py

Three idioms that every 2025-era Python codebase reaches for constantly:

    @dataclass   — the standard way to write classes that hold data
    StrEnum      — typed sets of string constants (3.11+)
    Decimal      — precise arithmetic for money, measurements, any domain
                   where "0.1 + 0.2 != 0.3" would be a bug

Each section is runnable and asserts its own results, so the guide fails
loudly if any claim here drifts out of date.

TABLE OF CONTENTS
  1. Why @dataclass exists                  (line ~40)
  2. frozen, slots, kw_only                 (line ~110)
  3. field(default_factory, init, compare)  (line ~180)
  4. StrEnum (3.11+) and IntEnum             (line ~240)
  5. Decimal for money                      (line ~320)
  6. Interview-style bugs each idiom fixes  (line ~410)
"""

from dataclasses import asdict, dataclass, field, replace
from decimal import ROUND_HALF_UP, Decimal, getcontext
from enum import IntEnum, StrEnum, auto


# ============================================================================
# 1. WHY @dataclass EXISTS
# ============================================================================
#
# Before @dataclass (pre-3.7), writing a data-holder class looked like this:
#
#     class Point:
#         def __init__(self, x, y):
#             self.x = x
#             self.y = y
#         def __repr__(self):
#             return f"Point(x={self.x!r}, y={self.y!r})"
#         def __eq__(self, other):
#             if not isinstance(other, Point):
#                 return NotImplemented
#             return (self.x, self.y) == (other.x, other.y)
#         def __hash__(self):
#             return hash((self.x, self.y))
#
# That's 10 lines of boilerplate per class, and almost every hand-written
# __eq__ I've seen in code review has at least one subtle bug
# (forgot a field, wrong inheritance check, wrong return value on mismatch).
#
# @dataclass generates the same methods for you — correctly, every time.


@dataclass
class Point:
    x: float
    y: float


def demo_why_dataclass() -> None:
    print("=" * 60)
    print("1. WHY @dataclass EXISTS")
    print("=" * 60)

    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)
    p3 = Point(1.0, 3.0)

    # Auto __repr__ — no more "<__main__.Point object at 0x...>" noise.
    assert repr(p1) == "Point(x=1.0, y=2.0)"
    # Auto __eq__ — field-by-field comparison.
    assert p1 == p2
    assert p1 != p3
    # Auto __init__ preserves positional and keyword calls.
    assert Point(3.0, 4.0) == Point(x=3.0, y=4.0)

    print(f"  Point(1.0, 2.0)      = {p1}")
    print(f"  p1 == p2             = {p1 == p2}")
    print(f"  p1 != p3             = {p1 != p3}")
    print(f"  asdict(p1)           = {asdict(p1)}")
    print("  Everything above is auto-generated from field declarations.\n")


# ============================================================================
# 2. frozen, slots, kw_only
# ============================================================================
#
# @dataclass takes several decorator arguments that unlock different
# behaviors.  The three most important:
#
#     frozen=True    — instances are immutable; assigning to a field raises.
#     slots=True     — __slots__ is generated; typos like obj.naem raise
#                      AttributeError instead of silently creating a new
#                      attribute.  Bonus: memory saving.
#     kw_only=True   — all fields are keyword-only; callers MUST use names.
#
# Pick them based on what you're modeling:
#   - A value object (money, coordinates, measurements):    frozen=True, slots=True
#   - A config struct with many fields:                     kw_only=True
#   - A domain entity you need to mutate:                   plain @dataclass


@dataclass(frozen=True, slots=True)
class Money:
    """An immutable, hashable money value."""
    amount: Decimal
    currency: str


@dataclass(slots=True)
class Sensor:
    """Mutable but slotted — typos raise AttributeError instead of
    silently creating a new attribute."""
    label: str
    reading: float


@dataclass(kw_only=True)
class DatabaseConfig:
    """Can't be constructed positionally — prevents ordering bugs."""
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True


def demo_frozen_slots_kw_only() -> None:
    print("=" * 60)
    print("2. frozen / slots / kw_only")
    print("=" * 60)

    usd = Money(Decimal("42.50"), "USD")
    print(f"  Money(42.50, USD)     = {usd}")

    # Immutable: this raises FrozenInstanceError.
    try:
        usd.amount = Decimal("0")  # type: ignore[misc]
    except Exception as exc:
        print(f"  usd.amount = 0        -> {type(exc).__name__}: {exc}")

    # Hashable: usable as a dict key or set member.
    prices = {Money(Decimal("10"), "USD"), Money(Decimal("10"), "USD")}
    assert len(prices) == 1, "frozen dataclasses deduplicate in sets"
    print(f"  {{Money(10, USD), Money(10, USD)}} has {len(prices)} item")

    # slots prevents typos from silently creating attributes.  Demonstrating
    # on a MUTABLE slotted class, so the frozen check doesn't trip first.
    s = Sensor(label="temp", reading=20.0)
    try:
        s.labl = "typo"  # type: ignore[attr-defined]
    except AttributeError as exc:
        print(f"  s.labl = 'typo'       -> AttributeError: {exc}")

    # kw_only: positional construction is blocked.
    try:
        DatabaseConfig("localhost", 5432, "u", "p")  # type: ignore[misc]
    except TypeError as exc:
        print(f"  positional kw_only    -> TypeError: {exc}")
    cfg = DatabaseConfig(host="localhost", port=5432, username="u", password="p")
    print(f"  DatabaseConfig(...)    = {cfg}")
    print()


# ============================================================================
# 3. field(default_factory, init, compare)
# ============================================================================
#
# Three flags on field() carry most of the per-field configuration you need:
#
#   default_factory  — call this to produce a fresh default value.  Use this
#                      for list/dict/set defaults.  Writing `tags: list[str]
#                      = []` raises ValueError at class definition time —
#                      Python refuses to let you make the mutable-default bug.
#
#   init=False       — don't include this field in __init__.  Useful for
#                      computed/cached state initialised in __post_init__.
#
#   compare=False    — ignore this field in the auto __eq__.  Useful for
#                      caches, timestamps, or audit fields that shouldn't
#                      affect equality.


@dataclass
class Cart:
    owner: str
    items: list[str] = field(default_factory=list)
    # An internal counter, never passed to __init__, not part of equality.
    _touch_count: int = field(default=0, init=False, compare=False)

    def add(self, item: str) -> None:
        self.items.append(item)
        self._touch_count += 1


def demo_field_helpers() -> None:
    print("=" * 60)
    print("3. field(default_factory, init=False, compare=False)")
    print("=" * 60)

    c1 = Cart("Ada")
    c2 = Cart("Ada")
    c1.add("book")
    c2.add("book")
    # Each instance got its own list.
    assert c1.items == ["book"]
    assert c2.items == ["book"]
    assert c1.items is not c2.items
    # _touch_count is not considered for equality — they still match.
    assert c1 == c2, "equality ignores _touch_count (compare=False)"
    # You can't pass _touch_count to __init__ — it's init=False.
    try:
        Cart("Bob", items=["x"], _touch_count=99)  # type: ignore[call-arg]
    except TypeError as exc:
        print(f"  Cart(..., _touch_count=99)  -> TypeError: {exc}")

    print(f"  c1 = {c1}")
    print(f"  c2 = {c2}")
    print(f"  c1 == c2  even though _touch_count differs: {c1 == c2}")
    print("  RULE: mutable defaults -> field(default_factory=list/dict/set).")
    print("  RULE: derived state    -> field(init=False, repr=False, ...).\n")


# ============================================================================
# 4. StrEnum (3.11+) AND IntEnum
# ============================================================================
#
# StrEnum's killer feature: its members ARE strings.  json.dumps serialises
# them naturally, HTTP headers compare correctly, and dict lookups keyed
# by string still work.  IntEnum is the same trick for integers.
#
# Use them ANY time you have a small set of allowed values that crosses a
# serialisation boundary (JSON, HTTP, logs, database columns).


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class HttpStatus(IntEnum):
    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500


class LogLevel(StrEnum):
    # auto() lowercases the member name — perfect for log-level strings.
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()


def demo_str_enum() -> None:
    print("=" * 60)
    print("4. StrEnum and IntEnum")
    print("=" * 60)

    # Interoperability with plain strings — no .value dance needed.
    assert OrderStatus.PAID == "paid"
    assert "paid" == OrderStatus.PAID
    print(f"  OrderStatus.PAID == 'paid'   -> {OrderStatus.PAID == 'paid'}")

    # Works in JSON-style serialisation.
    import json
    encoded = json.dumps({"status": OrderStatus.SHIPPED})
    assert encoded == '{"status": "shipped"}'
    print(f"  json.dumps(...status=...)    = {encoded}")

    # Decoding: StrEnum(...) works as a validator.
    try:
        OrderStatus("bogus")
    except ValueError as exc:
        print(f"  OrderStatus('bogus')         -> ValueError: {exc}")

    # auto() in StrEnum yields the lowercased member name.
    assert LogLevel.DEBUG == "debug"
    assert LogLevel.WARNING == "warning"
    print(f"  LogLevel.WARNING              = {LogLevel.WARNING!r}")

    # IntEnum: math works, but the type identity is preserved.
    assert HttpStatus.OK == 200
    assert HttpStatus.OK + 1 == 201
    print(f"  HttpStatus.OK + 1             = {HttpStatus.OK + 1}")

    # Exhaustiveness check with match/case — mypy can verify all cases.
    def stage_label(s: OrderStatus) -> str:
        match s:
            case OrderStatus.PENDING | OrderStatus.PAID:
                return "in-flight"
            case OrderStatus.SHIPPED | OrderStatus.DELIVERED:
                return "completed"
            case OrderStatus.CANCELLED:
                return "cancelled"
        # mypy flags a missing case here if you add a new status.
        # At runtime this is unreachable when `s` is a real OrderStatus.
        raise AssertionError(f"unreachable: {s}")

    assert stage_label(OrderStatus.PAID) == "in-flight"
    print(f"  stage_label(PAID)             = {stage_label(OrderStatus.PAID)!r}")
    print()


# ============================================================================
# 5. Decimal FOR MONEY
# ============================================================================
#
# float is not a number — it's a binary approximation of one.  For money,
# that's unacceptable:
#
#     >>> 0.1 + 0.2
#     0.30000000000000004
#     >>> round(2.675, 2)
#     2.67                 # banker's rounding; it's not wrong, it's different
#
# decimal.Decimal is arbitrary-precision base-10 arithmetic.  It's slower
# than float (usually by 30-100x for pure math, negligible for typical
# business logic) but gets every penny right.
#
# RULE OF THUMB: if users would notice a one-cent discrepancy, use Decimal.
# This includes e-commerce, accounting, tax, payroll, invoices, and most
# finance.  It does NOT include scientific computing (use float or numpy
# or if you need precision, fractions.Fraction for rationals).


def demo_decimal() -> None:
    print("=" * 60)
    print("5. Decimal for money")
    print("=" * 60)

    # The float gotcha.
    assert 0.1 + 0.2 != 0.3, "floats are not precise!"
    print(f"  float:  0.1 + 0.2 == 0.3       -> {0.1 + 0.2 == 0.3}")
    print(f"           actually = {0.1 + 0.2!r}")

    # Decimal gets it right — but you MUST construct from strings.
    # Decimal(0.1) captures the float's imprecision.  Decimal('0.1') doesn't.
    bad = Decimal(0.1) + Decimal(0.2)
    good = Decimal("0.1") + Decimal("0.2")
    print(f"  Decimal(0.1) + Decimal(0.2)    = {bad}")
    print(f"  Decimal('0.1') + Decimal('0.2') = {good}")
    assert good == Decimal("0.3")

    # Comparison is exact.
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")

    # Quantization — round to a specific number of cents.
    # ROUND_HALF_UP is the standard commercial rounding.
    price = Decimal("2.675")
    assert price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("2.68")
    print(f"  Decimal('2.675').quantize(0.01) = "
          f"{price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}")

    # Context: precision applies to multiplication and division.
    getcontext().prec = 28  # default is 28 significant digits; this is explicit
    total = Decimal("19.99") * 3
    assert total == Decimal("59.97")
    print(f"  Decimal('19.99') * 3           = {total}")

    # Division retains precision.  (Not everything divides cleanly.)
    third = Decimal("1") / Decimal("3")
    print(f"  Decimal(1) / Decimal(3)        = {third}")

    # DON'T do: mixing Decimal and float.
    # Decimal('0.1') + 0.2  raises TypeError in 3.11+.  Even without the
    # TypeError, mixing reintroduces the float imprecision.  Keep the
    # boundary clean: str/int -> Decimal at ingress, Decimal -> str at egress.
    try:
        _ = Decimal("0.1") + 0.2
    except TypeError as exc:
        print(f"  Decimal + float               -> TypeError: {exc}")
    print()


# ============================================================================
# 6. INTERVIEW-STYLE BUGS EACH IDIOM FIXES
# ============================================================================


def demo_bugs_these_prevent() -> None:
    print("=" * 60)
    print("6. Real bugs these idioms prevent")
    print("=" * 60)
    print("""
  @dataclass(frozen=True) — prevents:
    A caller mutates your domain object, and the change propagates to every
    other place holding a reference.  Classic "action at a distance" bug
    (see Guide 02 Section 8).  Frozen + hashable means it's safe to hand
    around.  Exercise 23 has a concrete version of this bug.

  @dataclass(slots=True) — prevents:
    obj.naem = "x"  silently creates a new attribute.  Every subsequent
    obj.name read returns the old value.  The test passes locally because
    setUp happens to write 'name' first; it fails in CI where test order
    differs.  slots turns this into an AttributeError at write time.

  field(default_factory=list) — prevents:
    The Python mutable-default-argument bug (Guide 01 Section 2), applied
    to dataclasses.  Dataclasses refuse to accept `tags: list[str] = []`
    at class definition; they make the bug unreachable.

  StrEnum — prevents:
    `if status == "pedning": ...` — a typo that silently never matches.
    With StrEnum, the typo is OrderStatus.PEDNING which raises
    AttributeError at import time.  You find out on module load, not
    when the one bad production order arrives.  Exercise 25 has this bug.

  Decimal — prevents:
    A customer's invoice is off by one cent because `0.1 + 0.2 !=
    0.3`.  They notice.  Legal notices.  The issue becomes a Jira ticket
    that's harder to fix than it would have been to use Decimal on day one.
    Exercise 24 has a concrete version.
    """)


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    demo_why_dataclass()
    demo_frozen_slots_kw_only()
    demo_field_helpers()
    demo_str_enum()
    demo_decimal()
    demo_bugs_these_prevent()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Reach for @dataclass first.  frozen + slots + kw_only are cheap")
    print("     guardrails that prevent whole classes of bugs.")
    print("  2. field(default_factory=...) is the ONLY right way to default a")
    print("     list/dict/set in a dataclass.")
    print("  3. StrEnum (3.11+) for values that cross a serialisation boundary.")
    print("     Enum / IntEnum for internal-only categorical data.")
    print("  4. Decimal for money — ALWAYS construct from strings, never floats.")
    print("     Use quantize() at egress to pin down precision.")
    print()
    print("  Next up:")
    print("    Exercise 23 — Dataclass Refactor      (frozen / default_factory)")
    print("    Exercise 24 — Money (Decimal)         (invoice precision bugs)")
    print("    Exercise 25 — Enum State Machine      (StrEnum transition bugs)")
    print()


if __name__ == "__main__":
    main()
