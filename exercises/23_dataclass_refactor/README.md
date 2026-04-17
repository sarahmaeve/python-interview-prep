# Exercise 23: Dataclass Refactor

A user-profile module already uses `@dataclass`, but not consistently or with the right flags. The implementation has **4 bugs** related to dataclass idioms.

## How to run the tests

```bash
cd exercises/23_dataclass_refactor
python3 -m unittest test_user_profile
```

Your goal is to edit `user_profile.py` until all tests pass. Do **not** modify the test file.

## What's inside

- `UserProfile` — a value object that the codebase treats as immutable.
- `AuditEntry` — a log entry whose timestamp should not affect equality.
- `UserDirectory` — a store of profiles with a `grant_role` operation.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

The docstrings describe the *intent*: "immutable", "treat as immutable", "produce a NEW profile". The code doesn't yet enforce that intent. What decorator flag would make the class actually refuse mutation? What field option would make a per-instance fresh default?

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. A plain `@dataclass` lets callers assign new field values. Check the `frozen` flag.
2. `x: datetime = datetime.now(...)` evaluates the expression ONCE at class definition, not per instance. See `dataclasses.field(default_factory=...)`.
3. `AuditEntry`'s auto-generated `__eq__` compares ALL fields. `field(..., compare=False)` excludes a field from equality and hashing.
4. `grant_role` mutates the stored profile in place. Use `dataclasses.replace` to produce a new profile and overwrite the directory's reference.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `@dataclass(frozen=True)` on `UserProfile`. Frozen dataclasses are also auto-hashable.
2. `created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))`.
3. `at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), compare=False)`.
4. In `grant_role`:
    ```python
    from dataclasses import replace
    new_profile = replace(profile, roles=profile.roles + (role,))
    self._users[user_id] = new_profile
    return new_profile
    ```

</details>

## Relevant reading

- `guides/02_classes_and_oop.py` — Section 9 (@dataclass) and Section 11 (@cached_property context)
- `guides/09_modern_data_types.py` — Sections 2–3 (frozen/slots/kw_only and field helpers)
