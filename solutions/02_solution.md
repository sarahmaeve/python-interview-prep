# Solution: Exercise 02 - Text Formatter

## Bugs Found

1. **`title_case`** -- Never capitalizes the first character. The loop only uppercases a character when the preceding character is a space (`i > 0 and output[i-1] == " "`), so index 0 stays lowercase.

2. **`truncate`** -- Result exceeds `max_length`. When truncation is needed, the code returns `text[:max_length] + "..."`, producing a string of length `max_length + 3`. The slice should be `text[:max_length - 3]`.

3. **`word_wrap`** -- Prepends a leading space on wrapped lines. When a word overflows to a new line, `current_line = " " + word` adds a spurious space. Should be `current_line = word`.

## Diagnosis Process

- **Bug 1:** `title_case("python")` should return `"Python"`. Tracing: `output[0]` is `"p"`, but `i > 0` is `False` at index 0, so it is never uppercased. The condition needs a special case for the first character.
- **Bug 2:** `truncate("Hello, World!", 10)` should return `"Hello, ..."` (length 10). Current code returns `"Hello, Wor..."` (length 13). The test `test_result_length_does_not_exceed_max` explicitly asserts `len(result) <= 20`.
- **Bug 3:** `word_wrap("aaa bbb ccc ddd", 7)` -- when `"ccc"` wraps, `current_line` becomes `" ccc"`. The test asserts `line == line.lstrip()` for every line, catching the leading space.

## The Fix

### Bug 1 -- `title_case`

```python
# Before
for i in range(len(output)):
    if i > 0 and output[i - 1] == " ":
        output[i] = output[i].upper()

# After
for i in range(len(output)):
    if i == 0 or output[i - 1] == " ":
        output[i] = output[i].upper()
```

### Bug 2 -- `truncate`

```python
# Before
return text[:max_length] + "..."

# After
return text[:max_length - 3] + "..."
```

### Bug 3 -- `word_wrap`

```python
# Before
current_line = " " + word

# After
current_line = word
```

## Why This Bug Matters

- **Bug 1 (boundary condition):** Off-by-one at the start of a sequence. Whenever you write a loop that checks a predecessor element, ask: "What happens at index 0?"
- **Bug 2 (accounting for added characters):** When appending a suffix like `"..."`, the total length must stay within the limit. This is a frequent source of UI/API bugs in pagination, message previews, and filenames.
- **Bug 3 (copy-paste from the join branch):** The space belongs in the "append to current line" branch, not the "start new line" branch. Tracing the two branches separately reveals the mismatch.

## Discussion

- Python's built-in `str.title()` handles basic title-casing but behaves unexpectedly with apostrophes (e.g., `"it's" -> "It'S"`). A manual approach gives more control.
- `truncate` could use `textwrap.shorten()` from the standard library, which also collapses whitespace.
- `word_wrap` mirrors `textwrap.wrap()`. The standard library version also handles words longer than `width` by breaking them mid-word, which this implementation does not attempt.
- An alternative for `truncate` when `max_length < 3` is to return just `"..."[:max_length]` -- worth considering for robustness.
