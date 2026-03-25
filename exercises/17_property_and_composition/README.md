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

## Hints (try without these first)

<details>
<summary>Hint 1</summary>
If you access a method without parentheses and get a <code>method object</code>
instead of a number, the method is probably missing a <code>@property</code>
decorator.
</details>

<details>
<summary>Hint 2</summary>
A <code>@property</code> getter alone makes the attribute read-only. To support
assignment (<code>obj.x = value</code>) you also need a <code>@x.setter</code>
method. Without it, assigning to the attribute overwrites the property entirely.
</details>

<details>
<summary>Hint 3</summary>
When you store objects in a dict for later retrieval, make sure the <em>value</em>
is the object itself, not one of its attributes.
</details>

<details>
<summary>Hint 4</summary>
If some sensors have no readings, their average is <code>None</code>. Mixing
<code>None</code> into <code>sum()</code> raises a <code>TypeError</code>.
Filter first, then aggregate.
</details>
