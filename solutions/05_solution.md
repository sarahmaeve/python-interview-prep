# Solution: Exercise 05 — Test Interpretation (User Validator)

## Bugs Found

1. **`validate_email`** — Only checks for `@`, never verifies that the domain part contains a `.`. The test `test_rejects_email_with_at_but_no_dot_in_domain` expects `"user@domain"` to return `False`.

2. **`validate_password`** — Uses `>` instead of `>=` for the length check. An 8-character password like `"passwor1"` is rejected because `len("passwor1") > 8` is `False`.

3. **`validate_username`** — Never checks that the first character is a letter. `"1alice"` passes because `isalnum()` is `True`, but `test_rejects_username_starting_with_digit` expects `False`.

4. **`validate_user`** — A bare `except` catches `KeyError` when a required field is missing and returns `False`. The test expects a `ValueError` with the missing field's name in the message.

## Diagnosis Process

- Read each test class and identify what the test asserts.
- Trace the code path for the specific input in each failing test.
- For bug 1: `"user@domain"` has `@` so `"@" in email` is `True`, but the test expects `False`.
- For bug 2: `len("passwor1")` is 8; `8 > 8` is `False`.
- For bug 3: `"1alice".isalnum()` is `True`; no `[0].isalpha()` guard exists.
- For bug 4: `user_dict["email"]` raises `KeyError`; the bare `except` catches it and returns `False` instead of raising `ValueError`.

## The Fix

### Bug 1 — `validate_email`
```python
# Before
return "@" in email

# After
if "@" not in email:
    return False
domain = email.split("@", 1)[1]
return "." in domain
```

### Bug 2 — `validate_password`
```python
# Before
if len(password) > 8 and any(ch.isdigit() for ch in password):

# After
if len(password) >= 8 and any(ch.isdigit() for ch in password):
```

### Bug 3 — `validate_username`
```python
# Before
return username.isalnum()

# After
return username[0].isalpha() and username.isalnum()
```

### Bug 4 — `validate_user`
```python
# Before
try:
    email = user_dict["email"]
    password = user_dict["password"]
    username = user_dict["username"]
except:
    return False

# After
for field in ("email", "password", "username"):
    if field not in user_dict:
        raise ValueError(f"Missing required field: {field}")
email = user_dict["email"]
password = user_dict["password"]
username = user_dict["username"]
```

## Why This Bug Matters

- **Off-by-one (`>` vs `>=`)** is one of the most common boundary bugs. Always test exact boundary values.
- **Bare `except`** catches everything including `KeyboardInterrupt` and `SystemExit`. Use specific exception types.
- **Incomplete validation** (email, username) shows why tests should cover negative cases, not just the happy path.

## Discussion

- The `validate_email` fix is intentionally minimal. A production validator would use a regex or the `email-validator` library.
- Bug 4 could also be fixed with `except KeyError as e: raise ValueError(...) from e` to preserve the exception chain, which is cleaner when you want to convert one exception type to another.
- Writing tests first (TDD) would have caught bugs 1-3 immediately, since the implementation would have been driven by the expected behavior.
