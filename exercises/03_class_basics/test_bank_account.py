import unittest
from bank_account import BankAccount


class TestBankAccount(unittest.TestCase):

    def test_initial_balance_default(self):
        account = BankAccount("Alice")
        self.assertEqual(account.get_balance(), 0)

    def test_initial_balance_custom(self):
        account = BankAccount("Bob", balance=500)
        self.assertEqual(account.get_balance(), 500)

    def test_deposit_increases_balance(self):
        account = BankAccount("Alice")
        account.deposit(100)
        self.assertEqual(account.get_balance(), 100)

    def test_withdraw_success_returns_true(self):
        account = BankAccount("Alice", balance=200)
        result = account.withdraw(50)
        self.assertTrue(result)
        self.assertEqual(account.get_balance(), 150)

    def test_withdraw_insufficient_funds_returns_false(self):
        account = BankAccount("Alice", balance=30)
        result = account.withdraw(100)
        self.assertFalse(result)
        self.assertEqual(account.get_balance(), 30)

    def test_deposit_records_transaction(self):
        account = BankAccount("Alice")
        account.deposit(250)
        self.assertIn("deposit:250", account.transaction_history)

    def test_withdraw_records_transaction(self):
        account = BankAccount("Alice", balance=300)
        account.withdraw(75)
        self.assertIn("withdraw:75", account.transaction_history)

    def test_independent_transaction_histories(self):
        a1 = BankAccount("Alice")
        a2 = BankAccount("Bob")
        a1.deposit(100)
        self.assertEqual(len(a1.transaction_history), 1)
        self.assertEqual(len(a2.transaction_history), 0)

    def test_transfer_moves_funds(self):
        sender = BankAccount("Alice", balance=500)
        receiver = BankAccount("Bob", balance=100)
        sender.transfer(receiver, 200)
        self.assertEqual(sender.get_balance(), 300)
        self.assertEqual(receiver.get_balance(), 300)

    def test_transfer_overdraw_prevented(self):
        sender = BankAccount("Alice", balance=50)
        receiver = BankAccount("Bob", balance=100)
        sender.transfer(receiver, 200)
        self.assertEqual(sender.get_balance(), 50)
        self.assertEqual(receiver.get_balance(), 100)


if __name__ == "__main__":
    unittest.main()
