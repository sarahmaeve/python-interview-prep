# Solution 19 --- Writing Tests with Mocks for `OrderService`

## TestPlaceOrder

### `test_successful_order`

```python
def test_successful_order(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)
    inventory.check_stock.return_value = 10
    inventory.reserve.return_value = "RES-1"
    payment.charge.return_value = "CHG-1"

    service = OrderService(payment, inventory)
    result = service.place_order("cust-1", "prod-1", 2, 25.0)

    self.assertEqual(result["status"], "confirmed")
    self.assertEqual(result["reservation_id"], "RES-1")
    self.assertEqual(result["charge_id"], "CHG-1")
```

**Technique:** Configure `return_value` on each mock method to simulate a happy path. **Assertions:** Checking all three dict keys ensures the return value is fully constructed from the mock outputs.

### `test_out_of_stock`

```python
def test_out_of_stock(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)
    inventory.check_stock.return_value = 1

    service = OrderService(payment, inventory)
    result = service.place_order("cust-1", "prod-1", 5, 25.0)

    self.assertEqual(result, {"status": "out_of_stock"})
    inventory.reserve.assert_not_called()
```

**Technique:** `assert_not_called()` verifies a side-effect did *not* happen. **Assertions:** Both the return value and the absence of `reserve` matter -- early exit must skip downstream work.

### `test_payment_failure_releases_reservation`

```python
def test_payment_failure_releases_reservation(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)
    inventory.check_stock.return_value = 10
    inventory.reserve.return_value = "RES-1"
    payment.charge.side_effect = Exception("card declined")

    service = OrderService(payment, inventory)
    result = service.place_order("cust-1", "prod-1", 2, 25.0)

    self.assertEqual(result, {"status": "payment_failed"})
    inventory.release.assert_called_once_with("RES-1")
```

**Technique:** `side_effect = Exception(...)` makes the mock raise on call. **Assertions:** The release call proves the cleanup branch ran, and the status proves the exception was caught.

### `test_correct_amount_charged`

```python
def test_correct_amount_charged(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)
    inventory.check_stock.return_value = 10
    inventory.reserve.return_value = "RES-1"
    payment.charge.return_value = "CHG-1"

    service = OrderService(payment, inventory)
    service.place_order("cust-1", "prod-1", 3, 10.0)

    payment.charge.assert_called_once_with("cust-1", 30.0)
```

**Technique:** `assert_called_once_with` verifies exact arguments. **Assertions:** Confirms the multiplication `quantity * price_per_unit` is computed correctly and passed to the payment client.

### `test_reserve_called_with_correct_args`

```python
def test_reserve_called_with_correct_args(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)
    inventory.check_stock.return_value = 10
    inventory.reserve.return_value = "RES-1"
    payment.charge.return_value = "CHG-1"

    service = OrderService(payment, inventory)
    service.place_order("cust-1", "prod-1", 4, 5.0)

    inventory.reserve.assert_called_once_with("prod-1", 4)
```

**Technique:** Argument inspection on the mock. **Assertions:** Ensures the product ID and quantity are forwarded correctly to the inventory client -- a common source of argument-ordering bugs.

---

## TestCancelOrder

### `test_successful_cancellation`

```python
def test_successful_cancellation(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)

    service = OrderService(payment, inventory)
    result = service.cancel_order("RES-1", "CHG-1")

    self.assertTrue(result)
    inventory.release.assert_called_once_with("RES-1")
    payment.refund.assert_called_once_with("CHG-1")
```

**Technique:** Default `MagicMock` methods return successfully without configuration. **Assertions:** `True` return plus both mock calls prove both cleanup steps ran.

### `test_failed_cancellation`

```python
def test_failed_cancellation(self):
    payment = MagicMock(spec=PaymentClient)
    inventory = MagicMock(spec=InventoryClient)
    inventory.release.side_effect = Exception("service down")

    service = OrderService(payment, inventory)
    result = service.cancel_order("RES-1", "CHG-1")

    self.assertFalse(result)
```

**Technique:** `side_effect` on one dependency simulates partial failure. **Assertions:** `False` proves the exception is caught and converted to a graceful return value.

---

## TestNotifyCustomer

### `test_sends_notification_successfully`

```python
@patch("order_service.urlopen")
def test_sends_notification_successfully(self, mock_urlopen):
    mock_urlopen.return_value.status = 200
    service = OrderService(MagicMock(), MagicMock())

    result = service.notify_customer("cust-1", "Your order shipped")

    self.assertTrue(result)
```

**Technique:** `@patch` replaces `urlopen` at the module level. **Assertions:** The return value `True` confirms the `status == 200` branch was taken.

### `test_sends_correct_payload`

```python
@patch("order_service.urlopen")
def test_sends_correct_payload(self, mock_urlopen):
    mock_urlopen.return_value.status = 200
    service = OrderService(MagicMock(), MagicMock())

    service.notify_customer("cust-1", "Hello")

    args, kwargs = mock_urlopen.call_args
    self.assertEqual(args[0], "https://notifications.example.com/send")
    import json
    payload = json.loads(args[1])
    self.assertEqual(payload["customer_id"], "cust-1")
    self.assertEqual(payload["message"], "Hello")
```

**Technique:** Inspecting `call_args` to examine the exact URL and JSON body. **Assertions:** Verifying the payload structure ensures the method serializes customer data correctly.

### `test_returns_false_on_non_200`

```python
@patch("order_service.urlopen")
def test_returns_false_on_non_200(self, mock_urlopen):
    mock_urlopen.return_value.status = 500
    service = OrderService(MagicMock(), MagicMock())

    result = service.notify_customer("cust-1", "Hello")

    self.assertFalse(result)
```

**Technique:** Configure mock to return a non-200 status. **Assertions:** `False` proves the method checks the status code and does not blindly return `True`.

---

## Mock Decisions

**Why PaymentClient and InventoryClient are mocked via dependency injection (not `@patch`):**
`OrderService.__init__` accepts both clients as constructor arguments. This is textbook dependency injection -- the test creates `MagicMock(spec=PaymentClient)` and passes it in directly. No patching is needed because the production code never imports or instantiates these clients itself. This approach is simpler, faster, and makes the dependency explicit in the test setup.

**Why `notify_customer` requires `@patch`:**
`notify_customer` calls `urlopen` directly -- it is imported at the top of `order_service.py` and used inline. There is no constructor parameter to swap it out. The only way to intercept it in a test is `@patch("order_service.urlopen")`, which replaces the name in the module's namespace for the duration of the test. This is the standard technique for code that calls global functions or library APIs that were not designed for injection.

**The general rule:** Prefer dependency injection when you control the design. Use `@patch` when you must mock something the code reaches for directly (stdlib calls, third-party APIs, module-level functions). Injection makes tests clearer; patching is the fallback for code you cannot restructure.
