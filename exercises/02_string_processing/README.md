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

## Principle Primer

String transformations are boundary-heavy. Check empty input, the first and
last character, and exact output-length guarantees. When adding a suffix, its
length counts toward the limit. When joining words into lines, treat separators
as separators rather than storing them as part of a word.

If you get stuck, use [HINTS.md](HINTS.md).
