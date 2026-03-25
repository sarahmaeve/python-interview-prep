# Solution: Exercise 12 -- Refactoring for Testability (Capstone)

This exercise demonstrates **dependency injection** -- the most important design pattern for testable code. Every bug stems from the same root cause: bypassing an injected dependency.

## Bugs Found

### Bug 1: `send_email` creates a new `SmtpClient` instead of using the injected one

**Location:** `send_email`, line 31

The constructor accepts `email_client`, but `send_email` ignores it and instantiates a fresh `SmtpClient()`.

**Diagnosis:** `test_email_sent_through_injected_client` passes a `MagicMock(spec=SmtpClient)` and asserts `mock_smtp.send.assert_called_once_with(...)`. Since a different object is used, the mock is never called.

**Before:**
```python
def send_email(self, to, subject, body):
    client = SmtpClient()
    client.send(to, subject, body)
```

**After:**
```python
def send_email(self, to, subject, body):
    self.email_client.send(to, subject, body)
```

**Why it matters:** This is the textbook dependency injection violation. Creating dependencies internally makes the class impossible to test in isolation and tightly couples it to a concrete implementation.

---

### Bug 2: `should_send` uses `datetime.datetime.now()` instead of the injected clock

**Location:** `should_send`, line 41

The constructor accepts a `clock` callable, but the method calls `datetime.datetime.now()` directly.

**Diagnosis:** `test_uses_injected_clock_not_system_time` passes a `MagicMock` returning a fixed datetime and asserts `fake_clock.assert_called_once()`. The mock is never called because the real system clock is used instead.

**Before:**
```python
now = datetime.datetime.now()
```

**After:**
```python
now = self.clock()
```

**Why it matters:** Time is a hidden dependency. Code that calls `datetime.now()` or `time.time()` directly is impossible to test deterministically. Injecting a clock callable makes tests fast, reliable, and timezone-independent.

---

### Bug 3: `format_message` uses wrong placeholder names

**Location:** `format_message`, line 49

The method calls `template.format(user_name=...)` (with underscore), but the test templates use `{username}` (no underscore). This causes a `KeyError` caught by the except clause, returning the fallback `"Notification message"`.

**Diagnosis:** `test_basic_template_formatting` passes template `"Hello {username}, ..."` and expects `"Hello Alice, ..."`. With `user_name` as the keyword argument, `{username}` is unresolved, triggering the `KeyError` fallback.

**Before:**
```python
formatted = template.format(user_name=data.get("username", ""),
                            order_id=data.get("order_id", ""),
                            balance=data.get("balance", ""))
```

**After:**
```python
formatted = template.format(username=data.get("username", ""),
                            order_id=data.get("order_id", ""),
                            balance=data.get("balance", ""))
```

**Why it matters:** The `try/except` silently hides the mismatch, making the bug hard to detect without tests. This is a cautionary tale about overly broad exception handling -- the fallback masks a real programming error.

---

### Bug 4: `send_batch` breaks on first failure

**Location:** `send_batch`, line 67

The `break` statement exits the loop when any recipient fails, skipping all remaining recipients.

**Diagnosis:** `test_continues_after_failure` sets up 3 recipients where the first fails. It expects `send.call_count == 3` and two successful deliveries. With `break`, only the first recipient is attempted.

**Before:**
```python
except Exception:
    failed.append(recipient)
    break
```

**After:**
```python
except Exception:
    failed.append(recipient)
```

Simply remove the `break`.

**Why it matters:** Batch operations should be resilient. One failure should not prevent delivery to other recipients. The `break` turns a partial failure into a total failure.

---

## Discussion

### The Dependency Injection Pattern

All four bugs illustrate what happens when code bypasses its own abstraction boundaries:

| Bug | Bypassed dependency | Fix |
|-----|---------------------|-----|
| 1 | `self.email_client` | Use the injected client |
| 2 | `self.clock` | Call the injected callable |
| 3 | Template contract | Match placeholder names to the API |
| 4 | Loop contract | Remove premature exit |

### Design Principles

1. **Constructor injection:** Accept dependencies in `__init__`, use them in methods. Never create collaborators inside business logic.
2. **Seams for testing:** Every external resource (network, filesystem, clock, randomness) should be injectable. This is what makes unit tests possible.
3. **Fail visibly:** The `try/except` in `format_message` hides bugs. Consider logging the original exception or narrowing the catch to only expected template errors.
4. **Resilient batch processing:** Collect errors and report them; don't abort the entire batch on the first failure.

### Alternative Approaches

- Instead of a `clock` callable, some codebases patch `datetime.datetime.now` with `freezegun`. Injection is more explicit and doesn't require patching.
- For `format_message`, using `template.format(**data)` would be more flexible but requires trusting the data keys. The explicit keyword approach is safer when the template vocabulary is fixed.
