# Hints: Exercise 11 — CSV Sales Report

## Hint 1

Trace the file handle and each product's running total on both success and
exception paths.

## Hint 2

Look for an open resource without structural cleanup, replacement where
accumulation is required, and an exception handler that continues with invalid
input.

## Hint 3

Open the input with a context manager, add each row's revenue to the existing
product total, and do not turn a missing input file into an empty report.

The complete walkthrough is in
[solutions/11_solution.md](../../solutions/11_solution.md).
