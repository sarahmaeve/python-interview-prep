# Solution 15 --- Writing Test Mocks for `PaymentProcessor`

## Group 1: Basic MagicMock with `spec` and `return_value`

### `test_successful_payment`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.charge.return_value = {"transaction_id": "tx_123", "status": "success"}
```

**Why:** `spec=PaymentGateway` restricts the mock to only the methods that `PaymentGateway` defines (`charge`, `refund`). Calling a misspelled method like `gateway.chrage(...)` would raise `AttributeError` instead of silently succeeding. `return_value` makes every call to `charge()` return the given dict.

### `test_refund_success`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.refund.return_value = True
```

**Why:** Same pattern -- `spec` guards against typos, and `return_value` provides a deterministic return value so we can assert `process_refund` propagates it correctly.

---

## Group 2: `side_effect` for Errors

### `test_gateway_error_returns_error_status`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.charge.side_effect = ConnectionError("Gateway down")
```

**Why:** Assigning an exception *instance* to `side_effect` makes the mock raise that exception whenever called. This simulates a network failure without needing a real gateway.

### `test_refund_gateway_failure`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.refund.side_effect = Exception("Service unavailable")
```

**Why:** Same technique -- we verify that `process_refund` catches the exception and returns `False` gracefully.

---

## Group 3: `side_effect` Lists (Sequences)

### `test_batch_processes_all_payments`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.charge.side_effect = [
    {"transaction_id": "tx_1", "status": "success"},
    ConnectionError("timeout"),
    {"transaction_id": "tx_3", "status": "success"},
]
```

**Why:** When `side_effect` is a *list*, each call to `charge()` consumes the next item. Dict items are returned; exception items are raised. This lets one mock simulate a realistic sequence of mixed outcomes across multiple calls.

### `test_log_records_all_outcomes`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.charge.side_effect = [
    {"transaction_id": "tx_1", "status": "success"},
    ConnectionError("refused"),
]
```

**Why:** Same list-based `side_effect`. We then inspect the processor's internal log to confirm both outcomes were recorded in order.

---

## Group 4: `assert_not_called` and Call Verification

### `test_fraud_threshold_skips_gateway`

```python
gateway = MagicMock(spec=PaymentGateway)
```

**Why:** No configuration is needed on `charge()` because the test verifies the method is *never called*. The assertion `gateway.charge.assert_not_called()` proves that the fraud-threshold short-circuit works. If `charge` were accidentally called, the test would fail.

---

## Group 5: `@patch` Decorator for Module-Level Imports

### `test_get_exchange_rate_patches_urlopen`

```python
mock_response = MagicMock()
mock_response.read.return_value.decode.return_value = '{"rate": 0.85}'
mock_urlopen.return_value = mock_response
```

**Why:** `urlopen` is imported at the top of `payment_processor.py`, so `@patch("payment_processor.urlopen")` replaces it in that module's namespace. We then build a mock response chain: calling `.read()` returns a mock whose `.decode()` returns a JSON string. This avoids any real HTTP call.

### `test_exchange_rate_with_context_manager_patch`

```python
with patch("payment_processor.urlopen") as mock_urlopen:
    mock_response = MagicMock()
    mock_response.read.return_value.decode.return_value = '{"rate": 1.25}'
    mock_urlopen.return_value = mock_response
    processor = PaymentProcessor(MagicMock(spec=PaymentGateway))
    rate = processor.get_exchange_rate("GBP")
```

**Why:** Identical concept to the decorator form, but using `with patch(...)` scopes the mock to the block. Everything that depends on the patch must happen inside the `with` block. Useful when only part of a test needs the patch.

---

## Group 6: `patch.object` for Instance Methods

### `test_international_payment_converts_currency`

```python
gateway = MagicMock(spec=PaymentGateway)
gateway.charge.return_value = {"transaction_id": "tx_intl", "status": "success"}

with patch.object(PaymentProcessor, "get_exchange_rate", return_value=0.85):
    processor = PaymentProcessor(gateway)
    result = processor.process_international_payment("tok_abc", 100, "EUR")
```

**Why:** `patch.object` replaces a single method on a class without affecting the rest. Here it prevents `get_exchange_rate` from calling `urlopen`, while still letting `process_payment` (and the gateway mock) work normally. The `return_value=0.85` keyword makes setup a one-liner.

---

## Quick Reference

| Concept | Key syntax |
|---|---|
| Restrict mock to real API | `MagicMock(spec=RealClass)` |
| Fixed return value | `mock.method.return_value = value` |
| Raise an exception | `mock.method.side_effect = SomeError("msg")` |
| Sequence of results | `mock.method.side_effect = [val1, Error("x"), val3]` |
| Patch a module-level name | `@patch("module.name")` or `with patch("module.name")` |
| Patch one method on a class | `patch.object(Class, "method", return_value=...)` |
| Chain calls (read/decode) | `mock.read.return_value.decode.return_value = "..."` |
| Verify never called | `mock.method.assert_not_called()` |
