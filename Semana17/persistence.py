import csv
from logic import Category, Transaction

def save_categories(categories, filename="categorias.csv"):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name"])
        for c in categories:
            writer.writerow([c.name])

def load_categories(filename="categorias.csv"):
    categories = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                categories.append(Category(row["name"]))
    except FileNotFoundError:
        pass
    return categories

def save_transactions(transactions, filename="transacciones.csv"):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "amount", "category", "type"])
        for t in transactions:
            writer.writerow([t.title, t.amount, t.category.name, t.type])

def load_transactions(categories, filename="transacciones.csv"):
    transactions = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = next((c for c in categories if c.name == row["category"]), None)
                if category:
                    transactions.append(Transaction(row["title"], float(row["amount"]), category, row["type"]))
    except FileNotFoundError:
        pass
    return transactions