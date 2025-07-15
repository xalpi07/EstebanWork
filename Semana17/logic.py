class Category:
    def __init__(self, name):
        self.name = name

class Transaction:
    def __init__(self, title, amount, category, type):
        self.title = title
        self.amount = amount
        self.category = category
        self.type = type  

class FinanceManager:
    def __init__(self):
        self.categories = []
        self.transactions = []

    def add_category(self, name):
        category = Category(name)
        self.categories.append(category)
        return category

    def add_transaction(self, title, amount, category_name, type):
        category = None
        for c in self.categories:
            if c.name == category_name:
                category = c
                break
        if category == None:
            raise ValueError("Category not found")
        transaction = Transaction(title, amount, category, type)
        self.transactions.append(transaction)
        return transaction

    def get_transactions(self):
        return self.transactions

    def get_categories(self):
        return self.categories

