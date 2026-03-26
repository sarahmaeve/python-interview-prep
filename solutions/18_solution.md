# Solution 18 --- Writing Tests for `StringCalculator`

## TestBasicAddition

### `test_empty_string_returns_zero`

```python
def test_empty_string_returns_zero(self):
    self.assertEqual(self.calc.add(""), 0)
```

**Why `assertEqual`:** The spec defines a single exact return value for empty input. **Edge case:** The degenerate input -- ensures the method handles "nothing" without crashing.

### `test_single_number_returns_its_value`

```python
def test_single_number_returns_its_value(self):
    self.assertEqual(self.calc.add("5"), 5)
```

**Why `assertEqual`:** One number has one correct sum. **Edge case:** No delimiter is present at all, so the split logic must still work with a single element.

### `test_two_numbers_comma_separated`

```python
def test_two_numbers_comma_separated(self):
    self.assertEqual(self.calc.add("1,2"), 3)
```

**Why `assertEqual`:** Verifies the most basic delimiter-and-sum path. **Edge case:** The minimal multi-number input; confirms comma splitting works.

### `test_multiple_numbers`

```python
def test_multiple_numbers(self):
    self.assertEqual(self.calc.add("1,2,3,4,5"), 15)
```

**Why `assertEqual`:** Proves the method sums an arbitrary-length list, not just pairs. **Edge case:** More than two numbers ensures the code loops, not just handles a special case.

---

## TestDelimiters

### `test_newline_as_delimiter`

```python
def test_newline_as_delimiter(self):
    self.assertEqual(self.calc.add("1\n2,3"), 6)
```

**Why `assertEqual`:** Mixing `\n` and `,` in one string must produce the same sum. **Edge case:** Mixed delimiters -- the method must treat newlines as equivalent to commas.

### `test_custom_delimiter`

```python
def test_custom_delimiter(self):
    self.assertEqual(self.calc.add("//;\n1;2;3"), 6)
```

**Why `assertEqual`:** The `//;\n` header declares `;` as the delimiter. **Edge case:** Tests the header-parsing branch that most inputs skip entirely.

---

## TestEdgeCases

### `test_negative_numbers_raise_value_error`

```python
def test_negative_numbers_raise_value_error(self):
    with self.assertRaises(ValueError) as ctx:
        self.calc.add("1,-2,3")
    self.assertIn("-2", str(ctx.exception))
```

**Why `assertRaises` + `assertIn`:** We need to confirm both that an exception is raised *and* that the message contains the offending number. **Edge case:** A single negative among positives.

### `test_multiple_negatives_all_listed`

```python
def test_multiple_negatives_all_listed(self):
    with self.assertRaises(ValueError) as ctx:
        self.calc.add("1,-2,3,-4")
    message = str(ctx.exception)
    self.assertIn("-2", message)
    self.assertIn("-4", message)
```

**Why two `assertIn` calls:** The spec requires *all* negatives in the error message, not just the first. **Edge case:** Multiple negatives verifies the code collects them all before raising.

### `test_numbers_over_1000_are_ignored`

```python
def test_numbers_over_1000_are_ignored(self):
    self.assertEqual(self.calc.add("2,1001"), 2)
```

**Why `assertEqual`:** 1001 is silently dropped; only 2 contributes. **Edge case:** The boundary just above 1000.

### `test_1000_is_not_ignored`

```python
def test_1000_is_not_ignored(self):
    self.assertEqual(self.calc.add("1000,2"), 1002)
```

**Why `assertEqual`:** 1000 itself is the boundary and must be included. **Edge case:** Off-by-one -- confirms the rule is "greater than 1000," not "greater than or equal to."

---

## Bonus Tests

```python
def test_custom_delimiter_with_numbers_over_1000(self):
    """Custom delimiter + ignore-over-1000 should combine correctly."""
    self.assertEqual(self.calc.add("//;\n1001;2"), 2)

def test_empty_string_with_custom_delimiter(self):
    """A custom-delimiter header followed by no numbers should still parse."""
    self.assertEqual(self.calc.add("//;\n0"), 0)

def test_negative_with_custom_delimiter(self):
    """Negatives should still be detected when using a custom delimiter."""
    with self.assertRaises(ValueError):
        self.calc.add("//;\n1;-2;3")
```

These bonus tests verify that features **compose** correctly -- custom delimiters interact with the over-1000 rule and the negatives rule. Interview-strength tests cover not just individual rules but their intersections.
