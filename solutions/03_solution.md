# Solution: Exercise 03 - Bank Account

## Bugs Found

1. **`transaction_history` is a mutable class attribute** -- Defined as `transaction_history = []` at class level, so all instances share the same list. Deposits on one account appear in every account's history.

2. **`withdraw` returns inverted booleans** -- Returns `True` on insufficient funds and `False` on success. The tests expect `True` for success, `False` for failure.

3. **`transfer` does not check the return value of `withdraw`** -- If the sender has insufficient funds, `withdraw` fails but `transfer` unconditionally calls `other_account.deposit(amount)`, crediting money from nowhere.

## Diagnosis Process

- **Bug 1:** `test_independent_transaction_histories` creates two accounts, deposits into one, and asserts the other's history has length 0. With a shared class-level list, both accounts see the same list, so `len(a2.transaction_history)` is 1.
- **Bug 2:** `test_withdraw_success_returns_true` calls `withdraw(50)` on an account with balance 200 and asserts `assertTrue(result)`. The code returns `False` on success. Similarly, `test_withdraw_insufficient_funds_returns_false` expects `False` but gets `True`.
- **Bug 3:** `test_transfer_overdraw_prevented` transfers 200 from an account with balance 50. The test expects the receiver's balance to stay at 100, but the buggy code deposits 200 into the receiver regardless.

## The Fix

### Bug 1 -- Mutable class attribute

```python
# Before
class BankAccount:
    transaction_history = []

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

# After
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.transaction_history = []
```

### Bug 2 -- Inverted return values in `withdraw`

```python
# Before
def withdraw(self, amount):
    if amount > self.balance:
        return True
    self.balance -= amount
    self.transaction_history.append(f"withdraw:{amount}")
    return False

# After
def withdraw(self, amount):
    if amount > self.balance:
        return False
    self.balance -= amount
    self.transaction_history.append(f"withdraw:{amount}")
    return True
```

### Bug 3 -- Unchecked withdraw in `transfer`

```python
# Before
def transfer(self, other_account, amount):
    self.withdraw(amount)
    other_account.deposit(amount)

# After
def transfer(self, other_account, amount):
    if self.withdraw(amount):
        other_account.deposit(amount)
```

## Why This Bug Matters

- **Bug 1 (mutable default at class level):** This is one of Python's most notorious gotchas. Mutable objects (`list`, `dict`, `set`) defined as class attributes are shared across all instances. Always initialize mutable state inside `__init__`.
- **Bug 2 (boolean semantics):** Swapped booleans are subtle because the code "works" without raising exceptions. Establish a clear convention -- success returns `True` -- and test both paths.
- **Bug 3 (ignoring return values):** Financial operations must be atomic: only credit the receiver if the debit succeeds. In production code, this pattern extends to database transactions and distributed systems.

## Discussion

- In real systems, `withdraw` might raise an `InsufficientFundsError` exception instead of returning a boolean, making it impossible to ignore the failure.
- `transfer` could be made atomic by checking the balance up front, but using the return value of `withdraw` avoids duplicating the validation logic.
- The mutable-class-attribute bug also appears with default mutable function arguments (`def f(items=[])`), which is the same underlying issue: a single mutable object shared across multiple call sites.
