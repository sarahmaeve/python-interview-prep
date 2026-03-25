# Solution: Exercise 04 - Shapes (Inheritance Bugs)

## Bugs Found

1. **`Square.resize`** -- Only updates `self.side` but not `self.width` and `self.height`. Since `area()` is inherited from `Rectangle` and uses `self.width * self.height`, the area remains based on the original dimensions.

2. **`Circle.area`** -- Computes circumference (`2 * pi * r`) instead of area (`pi * r^2`). The formula `self.radius * 2 * math.pi` is the circumference.

3. **`Shape.__str__`** -- References `self.area` (the method object) instead of `self.area()` (the method call). The resulting string contains something like `<bound method ...>` instead of a number.

## Diagnosis Process

- **Bug 1:** `test_square_resize` creates `Square(4)`, calls `resize(10)`, and expects `area() == 100`. After `resize`, `self.side = 10` but `self.width` and `self.height` remain `4`, so `area()` returns `16`.
- **Bug 2:** `test_circle_area` creates `Circle(5)` and expects `area() == math.pi * 25`. The current code returns `5 * 2 * math.pi = 31.4159...` while the expected value is `78.5398...`.
- **Bug 3:** `test_rectangle_str` expects `"Rectangle: area=12"`. Without the `()`, the f-string interpolates the method reference, producing a string like `"Rectangle: area=<bound method Rectangle.area ...>"`.

## The Fix

### Bug 1 -- `Square.resize`

```python
# Before
def resize(self, new_side):
    self.side = new_side

# After
def resize(self, new_side):
    self.side = new_side
    self.width = new_side
    self.height = new_side
```

### Bug 2 -- `Circle.area`

```python
# Before
def area(self):
    return self.radius * 2 * math.pi

# After
def area(self):
    return math.pi * self.radius ** 2
```

### Bug 3 -- `Shape.__str__`

```python
# Before
return f"{self.name}: area={self.area}"

# After
return f"{self.name}: area={self.area()}"
```

## Why This Bug Matters

- **Bug 1 (state inconsistency in subclasses):** When a subclass introduces an alias (`side`) for inherited attributes (`width`, `height`), mutations must keep all representations in sync. A better design is to override `area()` in `Square` to use `self.side`, or have `resize` delegate to the parent's attributes.
- **Bug 2 (wrong formula):** Domain logic bugs pass syntax checks and type checks silently. Unit tests with known values are the primary defense. Always verify mathematical formulas against a reference.
- **Bug 3 (forgetting to call a method):** In Python, referencing a method without `()` returns the method object instead of calling it. This is valid syntax, so no error is raised. The f-string happily converts it to its repr.

## Discussion

- **Square vs Rectangle (Liskov Substitution Principle):** The classic OOP debate. A `Square` that inherits from `Rectangle` violates LSP because a `Rectangle` user expects to set width and height independently. An alternative design uses composition or makes `Square` a standalone class.
- **Keeping state in sync:** `Square.resize` must update three attributes. A `@property` for `area` computed from `self.side` alone would eliminate the sync issue. Alternatively, override `area()` in `Square` to return `self.side ** 2`.
- **Method vs property for `area`:** Using `@property` would make `self.area` (without parens) work correctly in `__str__`, but changes the public API. Consistency across the class hierarchy matters more than either choice on its own.
- **Circle's formula:** A helpful mnemonic -- area has squared units (r^2), circumference has linear units (r). If you see `r` without a square, it is likely a perimeter formula.
