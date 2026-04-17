# Solution: Exercise 23 — Dataclass Refactor

## Bugs Found

1. **`UserProfile` is a plain `@dataclass`** — the docstring and tests treat it as an immutable value object, but nothing enforces that. Assignment to any field silently succeeds and can cause action-at-a-distance bugs.

2. **`UserProfile.created_at` uses a module-load-time default** — `datetime.now(timezone.utc)` is evaluated ONCE when the class is defined. Every instance constructed without an explicit `created_at` gets the SAME timestamp.

3. **`AuditEntry.at` is included in equality comparisons** — the auto-generated `__eq__` compares every field, so entries differing only in timestamp fail to match. The docstring specifically says equality should ignore the timestamp.

4. **`UserDirectory.grant_role` mutates the stored profile in place** — callers that previously retrieved a profile see their snapshot change under them.

## Diagnosis Process

- `test_assigning_a_field_raises_frozen_instance_error` fails because the dataclass allows mutation. The `frozen=True` flag enforces immutability and — as a bonus — makes the class hashable.
- `test_two_profiles_created_at_different_times_have_different_timestamps` fails because `datetime.now(timezone.utc)` is evaluated when Python imports the class, not on each `UserProfile(...)` call. This is the dataclass equivalent of the mutable-default-argument bug.
- `test_same_fields_different_times_compare_equal` fails because `__eq__` compares all fields, including `at`. `field(compare=False)` excludes a field from equality (and `__hash__`) while still generating it for `__init__` and `__repr__`.
- `test_previously_retrieved_profile_is_unchanged` fails because `profile.roles += (role,)` reassigns on the shared object. Once `UserProfile` is frozen, this line ALSO raises `FrozenInstanceError`, so fixing bug 1 forces you to fix bug 4.

## The Fix

### Bug 1 — `UserProfile` not frozen

```python
@dataclass(frozen=True)
class UserProfile:
    ...
```

### Bug 2 — `created_at` default evaluated at class-definition time

```python
created_at: datetime = field(
    default_factory=lambda: datetime.now(timezone.utc)
)
```

### Bug 3 — `at` field affects equality

```python
at: datetime = field(
    default_factory=lambda: datetime.now(timezone.utc),
    compare=False,
)
```

### Bug 4 — `grant_role` mutates the stored profile

```python
from dataclasses import replace

def grant_role(self, user_id: str, role: str) -> UserProfile:
    profile = self._users[user_id]
    new_profile = replace(profile, roles=profile.roles + (role,))
    self._users[user_id] = new_profile
    return new_profile
```

`dataclasses.replace` returns a copy with the named fields overridden, leaving the original untouched.

## Why This Bug Matters

- **Value-object immutability.** A frozen dataclass is hashable and safe to share. Once you accept that two profiles with equal fields are interchangeable, mutation stops making sense — and frozen makes that explicit. Pair with `slots=True` when memory matters.
- **`default_factory` vs. expression defaults.** Any expression with observable side effects — `datetime.now()`, `uuid.uuid4()`, `open(...)` — MUST use `default_factory`. The plain-default form is a dataclass analogue of Python's most famous gotcha (mutable default arguments).
- **`compare=False` (and `repr=False`).** Use them for cache fields, timestamps, internal counters — anything that is INCIDENTAL to the object's identity. Forgetting breaks `__eq__` in surprising ways at scale.
- **`dataclasses.replace`.** The idiomatic way to "mutate" an immutable instance. Pairs naturally with `frozen=True`.

## Discussion

- We used a `tuple[str, ...]` for `roles` rather than a frozenset. Both are hashable and immutable; tuples preserve insertion order, frozensets don't. For a grant-order-matters system, tuple is right.
- `AuditEntry` deliberately stays non-frozen: in real systems you'd likely want it appended-to-only, but making it frozen also requires hashability which isn't tested here. A stronger design is `@dataclass(frozen=True)` with `compare=False` on `at` — then `AuditEntry` goes into sets directly.
- If you had used a `StrEnum` or `Literal` for roles instead of strings, mypy could verify the set of valid role names at check time. That's a natural follow-up refactor, but out of scope here.
