# Exercise 17: Property Decorators and Composition

## Difficulty: Intermediate

## Context

You are building a temperature monitoring system. A `TemperatureSensor` records
readings in Celsius and exposes computed statistics through `@property`
decorators. A `MonitoringStation` aggregates several sensors using composition
(it *has* sensors, it is *not* a sensor).

The implementation in `temp_monitor.py` has **4 bugs** -- all related to
`@property` usage or composition patterns. The test file is correct; do NOT
modify it.

## Instructions

1. Run the tests: `python -m unittest test_temp_monitor -v`
2. You should see some tests fail (around 8-9 failures depending on cascade).
3. Read each failure, trace it back to `temp_monitor.py`, and fix the bug.
4. There are exactly 4 bugs to find. All fixes are small (one or two lines).

## Running the tests

```bash
cd exercises/17_property_and_composition
python -m unittest test_temp_monitor -v
```

## Principle Primer

A property exposes method-backed behavior through attribute syntax. A
getter-only property is read-only: assignment raises `AttributeError`; a setter
must be declared with `@name.setter`. Composition means retaining references to
the objects that perform the delegated behavior. When aggregating optional
values, define whether absence means “skip,” “zero,” or “no result.”

If you get stuck, use [HINTS.md](HINTS.md).
