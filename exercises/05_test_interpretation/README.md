# Exercise 05: Test Interpretation — User Validator

A teammate wrote a `user_validator` module with four functions for validating
user registration data: emails, passwords, usernames, and a combined
`validate_user` check.

The **tests are correct** and serve as the specification. The **implementation
has 4 bugs**. Your job is to read the tests carefully, understand what the code
*should* do, then find and fix each bug in `user_validator.py`.

## Functions

| Function | Purpose |
|---|---|
| `validate_email(email)` | Returns `True` if the email contains `@` with at least one `.` after the `@` |
| `validate_password(password)` | Returns `True` if length >= 8 and contains at least one digit |
| `validate_username(username)` | Returns `True` if alphanumeric, starts with a letter, 3-20 chars |
| `validate_user(user_dict)` | Validates all fields; raises `ValueError` with a descriptive message for missing or invalid fields |

## How to work through this exercise

1. Run the tests: `python3 -m unittest test_user_validator`
2. Read each failing test name and body — they tell you exactly what the
   correct behavior is.
3. Find and fix the 4 bugs in `user_validator.py`.
4. Re-run until all 14 tests pass.

There are exactly **4 bugs** to find.
