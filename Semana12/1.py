class BankAccount:
    def __init__(self, initial_balance):
        self.balance = initial_balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"${amount} deposited successfully. Current balance: ${self.balance}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds.")
        elif amount <= 0:
            print("Withdrawal amount must be positive.")
        else:
            self.balance -= amount
            print(f"${amount} withdrawn successfully. Current balance: ${self.balance}")

class SavingsAccount(BankAccount):
    def __init__(self, initial_balance, min_balance):
        BankAccount.__init__(self, initial_balance)  
        self.min_balance = min_balance

    def withdraw(self, amount):
        if self.balance - amount < self.min_balance:
            print(f"Withdrawal denied. Balance cannot go below the minimum balance of ${self.min_balance}.")
        else:
            BankAccount.withdraw(self, amount) 
            
account = BankAccount(100)
account.deposit(50)      
account.withdraw(30)     
account.withdraw(150)

savings_account = SavingsAccount(initial_balance=200, min_balance=50)
savings_account.deposit(100)
savings_account.withdraw(200)
savings_account.withdraw(150)