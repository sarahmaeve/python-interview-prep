# Hints: Exercise 26 — pathlib Bugs

## Hint 1

Inspect compound suffixes, the parent used in destination composition, and
whether discovery descends into subdirectories.

## Hint 2

`Path.stem` removes only one suffix; joining with a relative file can turn its
name into a directory; `glob("*")` is not recursive.

## Hint 3

Remove the complete suffix string from `source_file.name`, join through
`relative_file.parent`, and discover with `rglob("*")`.

The complete code is in
[solutions/26_solution.md](../../solutions/26_solution.md).
