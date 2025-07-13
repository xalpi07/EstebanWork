import PySimpleGUI as sg

from logic import Category, Transaction

def add_category_window():
    layout = [
        [sg.Text("Add Category")],
        [sg.Input(key="CATEGORY_NAME")],
        [sg.Button("Save"), sg.Button("Cancel")]
    ]
    window = sg.Window("Add Category", layout)
    event, values = window.read()
    window.close()
    if event == "Save":
        return values["CATEGORY_NAME"]
    return None

def add_transaction_window(categories, type_):
    layout = [
        [sg.Text(f"Add {type_.capitalize()}")],
        [sg.Text("Title"), sg.Input(key="TITLE")],
        [sg.Text("Amount"), sg.Input(key="AMOUNT")],
        [sg.Text("Category"), sg.Combo([c.name for c in categories], key="CATEGORY")],
        [sg.Button("Save"), sg.Button("Cancel")]
    ]
    window = sg.Window(f"Add {type_.capitalize()}", layout)
    event, values = window.read()
    window.close()
    if event == "Save":
        return {
            "title": values["TITLE"],
            "amount": values["AMOUNT"],
            "category": values["CATEGORY"],
            "type": type_
        }
    return None

def main_window(transactions=[], categories=[], finance_manager=None):
    headings = ["Title", "Amount", "Category", "Type"]
    table_data = [
        [t.title, t.amount, t.category.name, t.type] for t in transactions
    ]

    layout = [
        [sg.Text("Finance Manager", font=("Arial", 16))],
        [sg.Table(values=table_data, headings=headings, key="TABLE", auto_size_columns=True, justification="center", num_rows=10)],
        [sg.Button("Add Category"), sg.Button("Add Expense"), sg.Button("Add Income"), sg.Button("Exit")]
    ]

    window = sg.Window("Finance Manager", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break

        if event == "Add Category":
            category_name = add_category_window()
            if category_name:
                if finance_manager:
                    finance_manager.add_category(category_name)
                    categories = finance_manager.get_categories()
                else:
                    categories.append(Category(category_name))
                sg.popup("Category added!")
            # Actualizar la ventana principal si es necesario

        if event == "Add Expense":
            if not categories:
                sg.popup_error("No categories available. Please add a category first.")
                continue
            data = add_transaction_window(categories, "expense")
            if data:
                if finance_manager:
                    finance_manager.add_transaction(data["title"], float(data["amount"]), data["category"], data["type"])
                    transactions = finance_manager.get_transactions()
                else:
                    category_obj = next((c for c in categories if c.name == data["category"]), None)
                    transactions.append(Transaction(data["title"], float(data["amount"]), category_obj, data["type"]))
                sg.popup("Expense added!")
            # Actualizar la ventana principal si es necesario

        if event == "Add Income":
            if not categories:
                sg.popup_error("No categories available. Please add a category first.")
                continue
            data = add_transaction_window(categories, "income")
            if data:
                if finance_manager:
                    finance_manager.add_transaction(data["title"], float(data["amount"]), data["category"], data["type"])
                    transactions = finance_manager.get_transactions()
                else:
                    category_obj = next((c for c in categories if c.name == data["category"]), None)
                    transactions.append(Transaction(data["title"], float(data["amount"]), category_obj, data["type"]))
                sg.popup("Income added!")
            # Actualizar la ventana principal si es necesario

        # Actualizar la tabla después de cada cambio
        window["TABLE"].update(
            [[t.title, t.amount, t.category.name, t.type] for t in transactions]
        )

    window.close()

