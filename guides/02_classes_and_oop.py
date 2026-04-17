"""
Guide 02: Classes and Object-Oriented Programming
==================================================
Run this file:  python guides/02_classes_and_oop.py

This guide covers the OOP concepts and gotchas that appear most often in
Python interviews. Every section prints its own output.
"""

# ---------------------------------------------------------------------------
# 1. CLASS BASICS: __init__, INSTANCE ATTRIBUTES, CLASS ATTRIBUTES
# ---------------------------------------------------------------------------
# A class attribute is shared across ALL instances.
# An instance attribute is unique to each instance, set in __init__.

class Dog:
    species = "Canis familiaris"    # class attribute -- shared by all Dogs

    def __init__(self, name, age):
        self.name = name            # instance attribute -- per object
        self.age = age              # instance attribute -- per object

print("=== 1. Instance vs. Class Attributes ===")
buddy = Dog("Buddy", 9)
miles = Dog("Miles", 4)

print(f"  buddy.species = {buddy.species}")  # reads class attr via instance
print(f"  Dog.species   = {Dog.species}")     # reads class attr via class
print(f"  buddy.name    = {buddy.name}")      # instance attr

# Reassigning through an instance creates a NEW instance attribute that
# shadows the class attribute -- it does NOT change the class attribute.
buddy.species = "Canis lupus"
print(f"  After buddy.species = 'Canis lupus':")
print(f"    buddy.species = {buddy.species}")  # instance attr (shadow)
print(f"    miles.species = {miles.species}")   # still the class attr
print(f"    Dog.species   = {Dog.species}")     # unchanged
print()


# ---------------------------------------------------------------------------
# 2. MUTABLE CLASS ATTRIBUTE PITFALL
# ---------------------------------------------------------------------------
# This is a very common interview question. When a class attribute is
# mutable (like a list), ALL instances share the same object. Mutating it
# through one instance affects every other instance.

class StudentBroken:
    grades = []                   # shared mutable -- every instance sees this

    def __init__(self, name):
        self.name = name

    def add_grade(self, grade):
        self.grades.append(grade)  # mutates the shared list!

print("=== 2. Mutable Class Attribute Pitfall ===")
alice = StudentBroken("Alice")
bob = StudentBroken("Bob")

alice.add_grade(95)
bob.add_grade(72)

# CHALLENGE: What does alice.grades look like?
print(f"  alice.grades = {alice.grades}")
print(f"  bob.grades   = {bob.grades}")
# ANSWER: Both print [95, 72] because they share the same list.
print(f"  Same object?   {alice.grades is bob.grades}")  # True

# FIX: Initialize mutable attributes inside __init__ so each instance
# gets its own copy.
class StudentFixed:
    def __init__(self, name):
        self.name = name
        self.grades = []           # fresh list per instance

    def add_grade(self, grade):
        self.grades.append(grade)

alice2 = StudentFixed("Alice")
bob2 = StudentFixed("Bob")
alice2.add_grade(95)
bob2.add_grade(72)
print(f"  Fixed -- alice2.grades = {alice2.grades}")  # [95]
print(f"  Fixed -- bob2.grades   = {bob2.grades}")    # [72]
print()


# ---------------------------------------------------------------------------
# 3. METHOD RESOLUTION ORDER (MRO) AND super()
# ---------------------------------------------------------------------------
# When a class inherits from multiple parents, Python uses the C3
# linearization algorithm to determine the order in which classes are
# searched for a method. You can inspect it with ClassName.__mro__ or
# ClassName.mro().

class A:
    def who(self):
        return "A"

class B(A):
    def who(self):
        return "B"

class C(A):
    def who(self):
        return "C"

class D(B, C):
    pass            # does not override who()

print("=== 3. MRO and super() ===")
d = D()
print(f"  d.who() = {d.who()}")     # 'B' -- B comes before C in the MRO
print(f"  D.__mro__ = {[cls.__name__ for cls in D.__mro__]}")
# ['D', 'B', 'C', 'A', 'object']

# super() follows the MRO, which matters in cooperative multiple inheritance.
class Base:
    def __init__(self):
        print("    Base.__init__")

class Left(Base):
    def __init__(self):
        print("    Left.__init__")
        super().__init__()          # calls next in MRO, not necessarily Base

class Right(Base):
    def __init__(self):
        print("    Right.__init__")
        super().__init__()

class Child(Left, Right):
    def __init__(self):
        print("    Child.__init__")
        super().__init__()

print("  Cooperative __init__ chain:")
child = Child()
# Output order follows MRO: Child -> Left -> Right -> Base
print(f"  Child MRO: {[c.__name__ for c in Child.__mro__]}")
print()


# ---------------------------------------------------------------------------
# 4. __str__ VS __repr__
# ---------------------------------------------------------------------------
# __repr__: Unambiguous, aimed at developers. Used by repr() and the REPL.
#           Goal: could ideally be used to recreate the object.
# __str__:  Readable, aimed at end users. Used by str() and print().
# If only one is defined, define __repr__. Python falls back to __repr__
# when __str__ is not defined, but NOT the other way around.

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        # Developer-friendly: shows how to recreate the object.
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        # User-friendly: a clean display.
        return f"({self.x}, {self.y})"

print("=== 4. __str__ vs __repr__ ===")
p = Point(3, 7)
print(f"  print(p)  -> {p}")           # calls __str__: (3, 7)
print(f"  repr(p)   -> {repr(p)}")     # calls __repr__: Point(3, 7)

# Inside containers, Python uses __repr__ for the elements:
points = [Point(1, 2), Point(3, 4)]
print(f"  print(list) -> {points}")     # [Point(1, 2), Point(3, 4)]
print()

# --- __eq__ and __hash__ ---
# Defining __eq__ makes your objects comparable. But Python then sets
# __hash__ = None, making the object unhashable (can't use in sets or
# as dict keys).  If you need both, define __hash__ too.
#
#   class Point:
#       def __init__(self, x, y):
#           self.x, self.y = x, y
#       def __eq__(self, other):
#           return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
#       def __hash__(self):
#           return hash((self.x, self.y))


# ---------------------------------------------------------------------------
# 5. PROPERTY DECORATORS
# ---------------------------------------------------------------------------
# Properties let you add validation or computation to attribute access
# without changing the caller's syntax.

class Temperature:
    def __init__(self, celsius):
        # Uses the setter, which includes validation.
        self.celsius = celsius

    @property
    def celsius(self):
        """Read the temperature in Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is impossible.")
        self._celsius = value

    @property
    def fahrenheit(self):
        """Computed property -- no stored fahrenheit value."""
        return self._celsius * 9 / 5 + 32

print("=== 5. Property Decorators ===")
t = Temperature(25)
print(f"  {t.celsius}C = {t.fahrenheit}F")   # 25C = 77.0F

t.celsius = 100
print(f"  {t.celsius}C = {t.fahrenheit}F")   # 100C = 212.0F

# The setter prevents invalid values:
try:
    t.celsius = -300
except ValueError as e:
    print(f"  Caught: {e}")
print()


# ---------------------------------------------------------------------------
# 6. COMPOSITION VS. INHERITANCE
# ---------------------------------------------------------------------------
# Inheritance models "is-a": a Dog IS an Animal.
# Composition models "has-a": a Car HAS an Engine.
#
# Favor composition when:
#   - You only need SOME behavior from another class, not all of it.
#   - You want to swap implementations at runtime.
#   - Deep inheritance hierarchies become hard to follow.

# Inheritance example (appropriate: a clear "is-a" relationship)
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Subclasses must implement speak()")

# PREFERRED: use abc.ABC + @abstractmethod instead of NotImplementedError.
# This catches missing implementations at instantiation time, not at call time.
#
# from abc import ABC, abstractmethod
#
# class Animal(ABC):
#     @abstractmethod
#     def speak(self):
#         pass
#
# a = Animal()  # TypeError immediately -- can't instantiate abstract class
#
# NotImplementedError is the older pattern and only triggers when the
# method is actually called, meaning broken objects can exist silently.

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow"

# Composition example (appropriate: a Car is not an Engine)
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def start(self):
        return f"Engine ({self.horsepower}hp) started"

class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine           # Car HAS an Engine

    def start(self):
        return f"{self.model}: {self.engine.start()}"

print("=== 6. Composition vs. Inheritance ===")
cat = Cat("Whiskers")
print(f"  Inheritance: {cat.speak()}")

car = Car("Sedan", Engine(200))
print(f"  Composition: {car.start()}")

# Swapping implementations is easy with composition:
race_engine = Engine(500)
car.engine = race_engine
print(f"  Swapped engine: {car.start()}")
print()


# ---------------------------------------------------------------------------
# 7. PITFALL: FORGETTING super().__init__() IN SUBCLASSES
# ---------------------------------------------------------------------------
# If a subclass defines __init__ but forgets to call super().__init__(),
# the parent's initialization is skipped entirely. This can lead to
# AttributeError when you try to access attributes set by the parent.

class Vehicle:
    def __init__(self, make, year):
        self.make = make
        self.year = year

    def info(self):
        return f"{self.year} {self.make}"

# BROKEN: forgot to call super().__init__()
class TruckBroken(Vehicle):
    def __init__(self, make, year, payload):
        # super().__init__(make, year)   # <-- this line is missing!
        self.payload = payload

print("=== 7. Forgetting super().__init__() ===")
try:
    t_broken = TruckBroken("Ford", 2024, 1000)
    print(f"  t_broken.info() = {t_broken.info()}")
except AttributeError as e:
    print(f"  AttributeError: {e}")
    # 'TruckBroken' object has no attribute 'make'

# FIXED: always call super().__init__() to initialize the parent.
class TruckFixed(Vehicle):
    def __init__(self, make, year, payload):
        super().__init__(make, year)    # initialize Vehicle's attributes
        self.payload = payload

t_fixed = TruckFixed("Ford", 2024, 1000)
print(f"  Fixed: {t_fixed.info()}, payload={t_fixed.payload}kg")
print()


# ---------------------------------------------------------------------------
# FINAL CHALLENGE: PREDICT THE OUTPUT
# ---------------------------------------------------------------------------
# Combines several concepts from this guide. Try to figure it out before
# running the file.

class Counter:
    default_step = 1               # class attribute

    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value += self.default_step

    def __repr__(self):
        return f"Counter(value={self.value}, step={self.default_step})"

print("=== Final Challenge ===")
c1 = Counter()
c2 = Counter(10)

c1.increment()
c1.increment()

# This creates an INSTANCE attribute that shadows the class attribute.
c2.default_step = 5
c2.increment()

Counter.default_step = 3   # changes class attribute for everyone WITHOUT shadow

c1.increment()             # c1 has no shadow, so it picks up the new class attr

print(f"  c1 = {repr(c1)}")
print(f"  c2 = {repr(c2)}")
# ANSWER:
#   c1 = Counter(value=5, step=3)
#     - c1.value: 0 + 1 + 1 + 3 = 5  (third increment uses new class attr 3)
#     - c1.default_step: 3            (reads class attr, which was changed)
#   c2 = Counter(value=15, step=5)
#     - c2.value: 10 + 5 = 15         (used its instance shadow of 5)
#     - c2.default_step: 5            (instance attr shadows the class attr)


# ---------------------------------------------------------------------------
# 8. DEFENSIVE COPYING — PROTECTING INTERNAL STATE
# ---------------------------------------------------------------------------
# When a class stores a mutable object (list, dict, set), returning a
# direct reference to it lets callers mutate your internal state.
# This is a common source of "action at a distance" bugs.
#
# Rule: return a COPY, not the original.  Accept copies too, if the caller
# might mutate the argument later.

print("\n=== 8. Defensive Copying ===")


class TodoList:
    """Demonstrates the danger of exposing internal state."""

    def __init__(self):
        self._items = []

    def add(self, item):
        self._items.append(item)

    # BAD: returns the internal list directly
    def get_items_bad(self):
        return self._items

    # GOOD: returns a shallow copy — caller can't mutate our state
    def get_items_good(self):
        return list(self._items)

    def count(self):
        return len(self._items)


todo = TodoList()
todo.add("Buy milk")
todo.add("Write tests")

# --- The bad version leaks the reference ---
leaked = todo.get_items_bad()
leaked.append("INJECTED!")       # This mutates the INTERNAL list!
print(f"  After leaking: todo.count() = {todo.count()}")  # 3, not 2!

# --- The good version is safe ---
todo2 = TodoList()
todo2.add("Buy milk")
todo2.add("Write tests")
safe_copy = todo2.get_items_good()
safe_copy.append("INJECTED!")    # Only mutates the copy
print(f"  After copying: todo2.count() = {todo2.count()}")  # 2, correct!

# The same applies to dicts:
#   BAD:  return self._config
#   GOOD: return dict(self._config)
#
# And to accepting mutable arguments:
#   BAD:  self._tags = tags
#   GOOD: self._tags = list(tags)    # copy on the way IN, too

print("  Rule: return list(self._items), not self._items")
print("  Rule: copy mutable args in __init__ if the caller might change them")
print()


# ---------------------------------------------------------------------------
# 9. @dataclass -- THE MODERN WAY TO WRITE DATA CLASSES
# ---------------------------------------------------------------------------
# In Python 3.11+, @dataclass should be your first reach for any class that
# mostly carries data.  It auto-generates __init__, __repr__, __eq__, and
# optionally __hash__ and ordering methods — you don't have to write them.

from dataclasses import dataclass, field, replace

print("=== 9. @dataclass ===")


@dataclass
class Point:
    """A 2-D point.  __init__, __repr__, and __eq__ are auto-generated."""
    x: float
    y: float


p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
print(f"  Point(1.0, 2.0)         = {p1}")            # auto __repr__
print(f"  Point(1,2) == Point(1,2) = {p1 == p2}")      # auto __eq__
print(f"  Point(1,2).x            = {p1.x}")

# --- frozen=True: immutable + hashable ---
# A frozen dataclass raises FrozenInstanceError if you try to mutate it.
# That alone prevents a huge class of bugs (see exercise 23).  As a bonus,
# frozen instances are hashable, so they work as dict keys or set members.


@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float


c = Coordinate(37.77, -122.41)
try:
    c.lat = 0.0  # type: ignore[misc]
except Exception as e:
    print(f"  frozen mutation raised: {type(e).__name__}: {e}")
print(f"  hash(Coordinate(...))   = {hash(c) != 0}  (frozen dataclasses hash)")

# --- field(default_factory=...): the fix for mutable defaults ---
# Writing `tags: list[str] = []` in a dataclass raises ValueError at class
# definition time — Python forbids it because of the shared-default bug from
# Section 2.  Use field(default_factory=list) instead.


@dataclass
class Article:
    title: str
    tags: list[str] = field(default_factory=list)   # fresh list per instance


a1 = Article("First")
a2 = Article("Second")
a1.tags.append("draft")
print(f"  a1.tags = {a1.tags}, a2.tags = {a2.tags}   (independent)")

# --- kw_only=True (3.10+) ---
# Force keyword-only construction.  Prevents ordering bugs when a dataclass
# has many fields of the same type.


@dataclass(kw_only=True)
class EmailTemplate:
    subject: str
    body: str
    cc: str | None = None


# EmailTemplate("Hi", "Body")   # TypeError — positional not allowed
t = EmailTemplate(subject="Hi", body="Body")
print(f"  kw_only dataclass: {t}")

# --- slots=True (3.10+) ---
# Adds __slots__ for memory efficiency and to prevent accidental attribute
# creation (typos).


@dataclass(slots=True)
class Sensor:
    id: int
    name: str


s = Sensor(1, "temp")
try:
    s.labl = "typo"  # type: ignore[attr-defined]
except AttributeError as e:
    print(f"  slots dataclass caught typo: AttributeError: {e}")

# --- replace(): create a modified copy ---
# The idiomatic way to "mutate" a frozen dataclass is to produce a new one.
c2 = replace(c, lat=40.0)
print(f"  replace(c, lat=40.0)    = {c2}")
print("  RULE: reach for @dataclass first; only write __init__ by hand when")
print("  you need behavior dataclasses don't give you.\n")


# ---------------------------------------------------------------------------
# 10. Enum AND StrEnum — TYPED SET OF ALLOWED VALUES
# ---------------------------------------------------------------------------
# When a field can only take a handful of values, use an Enum.  String
# constants like "pending" / "completed" invite typos; Enums make them
# impossible: Status.PENDNIG raises AttributeError at import time.

from enum import Enum, StrEnum, auto

print("=== 10. Enum and StrEnum ===")


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


print(f"  Priority.HIGH         = {Priority.HIGH}")
print(f"  Priority.HIGH.value   = {Priority.HIGH.value}")
print(f"  Priority.HIGH.name    = {Priority.HIGH.name}")
print(f"  list(Priority)        = {list(Priority)}")

# StrEnum (Python 3.11+) — members compare equal to plain strings.  This
# is the sweet spot for protocol-level enums (JSON, HTTP headers, log
# levels, status flags): serialise naturally but still catch typos.


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


s = OrderStatus.PAID
print(f"  OrderStatus.PAID       = {s}            (is equal to 'paid': {s == 'paid'})")
print(f"  json.dumps serializes  = {s.value!r}")

# auto() lets you skip the values when they don't matter.


class Side(Enum):
    LEFT = auto()
    RIGHT = auto()


print(f"  auto() values          = {[s.value for s in Side]}")

# Pattern: match on an Enum — mypy verifies exhaustiveness when combined
# with typing.assert_never (see Guide 07).


def next_status(s: OrderStatus) -> OrderStatus:
    match s:
        case OrderStatus.PENDING:  return OrderStatus.PAID
        case OrderStatus.PAID:     return OrderStatus.SHIPPED
        case OrderStatus.SHIPPED | OrderStatus.CANCELLED:
            return s


print(f"  next_status(PENDING)   = {next_status(OrderStatus.PENDING)}")
print("  RULE: reach for StrEnum when values hit a protocol (JSON/HTTP/logs).")
print("  Reach for Enum when the values are internal and typos would hurt.\n")


# ---------------------------------------------------------------------------
# 11. @cached_property — COMPUTE ONCE, REMEMBER
# ---------------------------------------------------------------------------
# functools.cached_property turns expensive computations into attributes
# that run on first access and cache the result.  Use it when:
#   - The computation depends only on immutable instance state.
#   - The result would be identical across calls.
#   - Computing it is non-trivial (a loop, a network call, a big sum).

from functools import cached_property

print("=== 11. @cached_property ===")


class DatasetStats:
    """Computes statistics from a list of numbers — lazily and once."""

    def __init__(self, values: list[float]) -> None:
        self._values = list(values)  # defensive copy

    @cached_property
    def mean(self) -> float:
        print("    (mean computed)")
        return sum(self._values) / len(self._values)

    @cached_property
    def total(self) -> float:
        print("    (total computed)")
        return sum(self._values)


d = DatasetStats([1.0, 2.0, 3.0, 4.0])
print(f"  d.mean  = {d.mean}   (first access — computes)")
print(f"  d.mean  = {d.mean}   (second access — cached, no recompute)")
print(f"  d.total = {d.total}")

# Gotcha: @cached_property writes to self.__dict__.  If __slots__ is in use
# WITHOUT including the attribute, the write fails with AttributeError.
# For dataclasses with slots=True, add the cached_property name to __slots__
# or skip slots on that class.
print("  WARNING: @cached_property + __slots__ needs the name in __slots__.\n")


# ---------------------------------------------------------------------------
# SUMMARY OF INTERVIEW TAKEAWAYS
# ---------------------------------------------------------------------------
# - Class attributes are shared; instance attributes are per-object.
# - Mutating a shared mutable class attribute affects all instances.
# - MRO controls method lookup order; super() follows it cooperatively.
# - Define __repr__ for developers, __str__ for end users.
# - Use @property for validation and computed attributes.
# - Prefer composition ("has-a") over inheritance when the relationship
#   is not a natural "is-a".
# - Always call super().__init__() in subclasses to avoid missing attrs.
# - Return copies of internal mutable state, not direct references.
# - Reach for @dataclass (frozen/slots/kw_only) before writing __init__ by hand.
# - Reach for StrEnum (3.11+) when a field has a small set of allowed values.
# - @cached_property = "compute once, remember" for expensive read-only props.

print("=== All sections complete. ===")
