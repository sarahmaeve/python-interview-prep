# Exercise 03: Class Basics — Bank Account

A simple `BankAccount` class that tracks an owner, balance, and transaction history.

## Your Task

The file `bank_account.py` contains **3 bugs**. Run the tests with:

```bash
python3 -m unittest test_bank_account
```

All 10 tests should pass once every bug is fixed. Read the test file to understand the expected behavior, find the bugs, and fix them.

## Principle Primer

Per-account state belongs on each instance, normally initialized in
`__init__`; mutable state stored on the class is shared by every instance.
Method return values are part of the contract, especially when one operation
coordinates several others. For a multi-step operation, decide what should
happen when an early step fails before allowing later steps to run.

If you get stuck, use [HINTS.md](HINTS.md).
