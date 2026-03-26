class BankAccount:
    transaction_history = []

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append(f"deposit:{amount}")

    def withdraw(self, amount):
        if amount > self.balance:
            return True
        self.balance -= amount
        self.transaction_history.append(f"withdraw:{amount}")
        return False

    def get_balance(self):
        return self.balance

    def transfer(self, other_account, amount):
        self.withdraw(amount)
        other_account.deposit(amount)
