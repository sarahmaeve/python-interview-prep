# Exercise 20: Data Pipeline

## Problem

You are building a composable data transformation pipeline. The pipeline accepts a list of records (dicts) and applies a chain of transformation functions in order.

This exercise practices: **higher-order functions, closures, function composition, and the LEGB scope rule**.

## Constraints

- Each transformation is a callable that takes a single record (dict) and returns a transformed record (or `None` to filter it out)
- The pipeline should be composable — you can chain pipelines together
- Implement using functions (not classes) where possible
- No external libraries

## Your Task

Open `pipeline.py` and implement each function. The docstrings describe the expected behavior.

## Example Usage

```python
pipeline = create_pipeline(
    make_default("country", "Unknown"),
    make_field_mapper("name", str.upper),
    make_filter(lambda r: r["age"] >= 18),
)

records = [
    {"name": "alice", "age": 30},
    {"name": "bob", "age": 15},
    {"name": "carol", "age": 25, "country": "Canada"},
]

results = run_pipeline(pipeline, records)
# [
#   {"name": "ALICE", "age": 30, "country": "Unknown"},
#   {"name": "CAROL", "age": 25, "country": "Canada"},
# ]
```

## Testing

There are no pre-written tests. Consider writing your own to verify your pipeline works.

## Hints (only if you're stuck)

<details>
<summary>Hint 1</summary>
Think about what `create_pipeline` should return — it's a function. What does that function need to do with each transform?
</details>

<details>
<summary>Hint 2</summary>
`make_field_mapper` and `make_filter` each return a closure that captures `field`/`func` or `predicate` from the enclosing scope — this is the LEGB rule in action.
</details>

<details>
<summary>Hint 3</summary>
To avoid mutating the original record in `make_field_mapper`, use `{**record, field: new_value}` to create a new dict.
</details>
