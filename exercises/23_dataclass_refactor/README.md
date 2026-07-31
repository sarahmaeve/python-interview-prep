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

## Principle Primer

Dataclass options should encode the domain contract. Immutability belongs in
the class definition, per-instance dynamic defaults need a factory, and fields
that are metadata rather than identity may need exclusion from equality.
Updating an immutable value means constructing a replacement and updating the
owner's reference.

If you get stuck, use [HINTS.md](HINTS.md).

## Relevant reading

- `guides/02_classes_and_oop.py` — Section 9 (@dataclass) and Section 11 (@cached_property context)
- `guides/09_modern_data_types.py` — Sections 2–3 (frozen/slots/kw_only and field helpers)
