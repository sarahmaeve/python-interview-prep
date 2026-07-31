# Hints: Exercise 30 — Pytest Translation

## Hint 1

Start with the shared monitor fixture, then translate simple assertions before
the parametrized and filesystem cases.

## Hint 2

Use `@pytest.fixture`, plain `assert`, `pytest.raises`, parametrization, and
`tmp_path` according to the mapping in the README.

## Hint 3

The monitor fixture returns `TemperatureMonitor(low_threshold=0,
high_threshold=100)`. A complete translation is in
[solutions/30_solution.md](../../solutions/30_solution.md).
