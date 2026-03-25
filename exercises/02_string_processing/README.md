# Exercise 02: String Processing

A text formatting utility with three functions for transforming strings. The implementation has **3 bugs** for you to find and fix.

## How to run the tests

```bash
cd exercises/02_string_processing
python3 -m unittest test_text_formatter
```

Your goal is to edit `text_formatter.py` until all tests pass. Do **not** modify the test file.

## Functions

- `title_case(text)` — convert a string to title case (capitalize the first letter of every word).
- `truncate(text, max_length)` — shorten text to at most `max_length` characters, appending `"..."` when truncated.
- `word_wrap(text, width)` — insert newlines so no line exceeds `width` characters, breaking at spaces.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>
Look carefully at boundary conditions: the very first character, the total length after modification, and what happens at each line break.
</details>

<details>
<summary>Hint 2 (moderate)</summary>
One function forgets about index 0. Another produces output longer than requested. The third leaves unwanted whitespace.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `title_case`: The loop capitalizes letters that follow a space, but never capitalizes the first character of the string.
2. `truncate`: When the text is too long, it appends `"..."` *after* taking `max_length` characters, so the result is `max_length + 3` characters. It should slice to `max_length - 3` before appending.
3. `word_wrap`: When starting a new line, the code prepends a space to the next word, leaving a leading space on every wrapped line.

</details>
