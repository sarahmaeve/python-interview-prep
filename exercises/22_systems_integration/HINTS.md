# Hints: Exercise 22 — Systems Integration

## Hint 1

Trace each configured value to the operation it is intended to control.

## Hint 2

Check the `urlopen` arguments, when the default configuration is evaluated, and
whether `health_check()` uses the client's injected configuration.

## Hint 3

Pass the configured timeout to `urlopen`, resolve default configuration during
client construction rather than definition, and use `self.config["is_ci"]`
instead of reading the environment again.

The complete walkthrough is in
[solutions/22_solution.md](../../solutions/22_solution.md).
