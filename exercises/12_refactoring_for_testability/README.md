# Exercise 12: Notification Service (Capstone)

A notification service that sends emails and SMS messages, with scheduling and batch support. The implementation has **4 bugs** for you to find and fix. This is the hardest exercise in the series.

This exercise emphasizes **dependency injection and testability**. The constructor accepts injectable dependencies (email client, SMS client, clock), enabling tests to swap in mocks without patching. Study the test file to understand how dependency injection makes code easier to test and reason about.

## How to run the tests

```bash
cd exercises/12_refactoring_for_testability
python3 -m unittest test_notification_service
```

Your goal is to edit `notification_service.py` until all tests pass. Do **not** modify the test file.

## Classes

### SmtpClient (stub)
- `send(self, to, subject, body)` -- sends an email.

### SmsGateway (stub)
- `send_sms(self, to, message)` -- sends an SMS message.

### NotificationService
- `__init__(self, email_client=None, sms_client=None, clock=None)` -- accepts injectable dependencies for email, SMS, and a clock function.
- `send_email(self, to, subject, body)` -- sends an email through the injected client.
- `send_sms(self, to, message)` -- sends an SMS through the injected client.
- `should_send(self, schedule)` -- checks if the current hour (from the injected clock) falls within `schedule["start_hour"]` and `schedule["end_hour"]`.
- `format_message(self, template, data)` -- formats a template string using a data dict (e.g., `"Hello {username}"` with `{"username": "Alice"}` produces `"Hello Alice"`).
- `send_batch(self, recipients, message)` -- sends `message` to every recipient via email, returning `{"sent": [...], "failed": [...]}`. Must attempt **all** recipients even if some fail.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>
Does send_email actually use the client you passed into the constructor?
</details>

<details>
<summary>Hint 2 (moderate)</summary>
The clock dependency is accepted but is it used where time checks happen?
</details>

<details>
<summary>Hint 3 (moderate)</summary>
Compare the template placeholder names with the data dictionary keys very carefully.
</details>

<details>
<summary>Hint 4 (specific)</summary>

1. `send_email` creates a new `SmtpClient()` instead of using `self.email_client`.
2. `should_send` calls `datetime.datetime.now()` instead of `self.clock()`.
3. `format_message` uses `{user_name}` in the format call but the data dict key is `"username"` (no underscore). The `KeyError` is silently caught and a generic fallback is returned.
4. `send_batch` has a `break` after catching an exception, stopping at the first failure instead of continuing to the remaining recipients.

</details>
