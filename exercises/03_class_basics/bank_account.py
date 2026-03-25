class BankAccount:
    # BUG 1: transaction_history is a class attribute shared by all instances.
    # It should be initialized in __init__ as self.transaction_history = [].
    transaction_history = []

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append(f"deposit:{amount}")

    def withdraw(self, amount):
        if amount > self.balance:
            # BUG 2: Returns True on failure (should return False).
            return True
        self.balance -= amount
        self.transaction_history.append(f"withdraw:{amount}")
        # BUG 2 continued: Returns False on success (should return True).
        return False

    def get_balance(self):
        return self.balance

    def transfer(self, other_account, amount):
        # BUG 3: Doesn't check the return value of withdraw.
        # If withdraw fails (insufficient funds), it still deposits
        # into the other account.
        self.withdraw(amount)
        other_account.deposit(amount)
