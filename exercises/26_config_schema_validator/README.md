# Exercise 26: Config Schema Validator

## Difficulty: Intermediate

## Context

You are building a typed configuration validation system. Real-world tools
like Pydantic, Cerberus, and Marshmallow do this at scale — here you build
a minimal version from scratch using only the standard library.

Given a **schema** (a list of `FieldSchema` objects) and a **config** dict,
validate that the config matches the schema. Collect **all** errors in one
pass rather than stopping at the first problem.

## What you need to implement

Open `validator.py`. The dataclasses are already defined for you.
Implement the function:

### `validate(config, schema) -> ValidationResult`

For each `FieldSchema` in `schema`:

1. **Required check** — if `required=True` and the key is missing from
   `config`, add a `ValidationError`.
2. **Type check** — if the key is present, use `isinstance` to confirm the
   value matches `expected_type`. Add an error if not.
3. **Custom validator** — if `validator` is set and the type check passed,
   call `validator(value)`. Add an error if it returns `False`.
4. **Defaults** — if `required=False` and the key is absent, add it to the
   output config with the schema's `default` value.

Return a `ValidationResult` where:
- `is_valid` is `True` only when `errors` is empty.
- `config` is the input config dict with any defaults filled in.
  Return an empty dict if `is_valid` is `False`.

## Instructions

1. Run the tests to confirm they all pass trivially (all stubs, no assertions):
   ```bash
   cd exercises/26_config_schema_validator
   python3 -m unittest test_validator -v
   ```
2. Fill in the `TODO` stubs in `test_validator.py` — add the assertions for
   each test case as described in the docstrings.
3. Implement `validate` in `validator.py` until all tests pass.

## Constraints

- Use only the Python standard library (no Pydantic, Cerberus, etc.).
- Use `isinstance` for type checking (not `type(value) == ...`).
- Do **not** stop at the first error — collect them all.

## Running the tests

```bash
cd exercises/26_config_schema_validator
python3 -m unittest test_validator -v
```

## Hints (try without these first)

<details>
<summary>Hint 1 — overall structure of validate()</summary>

```python
def validate(config, schema):
    errors = []
    out = dict(config)  # start with a copy

    for field_schema in schema:
        key = field_schema.name
        if key not in config:
            if field_schema.required:
                errors.append(ValidationError(key, f"'{key}' is required"))
            else:
                out[key] = field_schema.default
            continue
        # type check, then custom validator ...

    if errors:
        return ValidationResult(is_valid=False, errors=errors, config={})
    return ValidationResult(is_valid=True, errors=[], config=out)
```
</details>

<details>
<summary>Hint 2 — writing the test stubs</summary>
Each test follows the same pattern:

```python
schema = [FieldSchema("host", str, required=True)]
config = {}  # deliberately missing "host"
result = validate(config, schema)
self.assertFalse(result.is_valid)
self.assertEqual(len(result.errors), 1)
self.assertEqual(result.errors[0].field, "host")
```
</details>
