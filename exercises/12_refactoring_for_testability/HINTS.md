# Hints: Exercise 12 — Notification Service

## Hint 1

Trace every collaborator accepted by the constructor to the call site where it
should be used.

## Hint 2

Check the email client, the clock, template-key spelling, and what happens to
later recipients after one send fails.

## Hint 3

Use `self.email_client`, call `self.clock()`, pass the template the exact
`"username"` key it expects, and continue the batch after recording a failed
recipient.

The complete walkthrough is in
[solutions/12_solution.md](../../solutions/12_solution.md).
