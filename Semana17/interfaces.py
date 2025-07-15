import PySimpleGUI as sg
from persistence import save_categories, save_transactions, load_categories, load_transactions

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

def add_transaction_window(categories, type):
    layout = [
        [sg.Text(f"Add {type}")],
        [sg.Text("Title"), sg.Input(key="TITLE")],
        [sg.Text("Amount"), sg.Input(key="AMOUNT")],
        [sg.Text("Category"), sg.Combo([c.name for c in categories], key="CATEGORY")],
        [sg.Button("Save"), sg.Button("Cancel")]
    ]
    window = sg.Window(f"Add {type}", layout)
    event, values = window.read()
    window.close()
    if event == "Save":
        return {
            "title": values["TITLE"],
            "amount": values["AMOUNT"],
            "category": values["CATEGORY"],
            "type": type
        }
    return None

def main_window(finance_manager):
    categories = load_categories()
    for c in categories:
        finance_manager.add_category(c.name)
    transactions = load_transactions(finance_manager.get_categories())
    for t in transactions:
        finance_manager.add_transaction(t.title, t.amount, t.category.name, t.type)

    headings = ["Title", "Amount", "Category", "Type"]
    table_data = [
        [t.title, t.amount, t.category.name, t.type] for t in finance_manager.get_transactions()
    ]

    layout = [
        [sg.Text("Finance Manager")],
        [sg.Table(
            values=table_data,
            headings=headings,
            key="TABLE",
            auto_size_columns=False,
            col_widths=[25, 10, 15, 10], 
            justification="center",
            num_rows=10,
            expand_x=True,
            expand_y=True
        )],
        [sg.Button("Add Category"), sg.Button("Add Expense"), sg.Button("Add Income"), sg.Button("Exit")]
    ]

    window = sg.Window("Finance Manager", layout, resizable=True, size=(600, 400))

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break

        if event == "Add Category":
            category_name = add_category_window()
            if category_name:
                finance_manager.add_category(category_name)
                save_categories(finance_manager.get_categories())
                sg.popup("Category added!")

        if event == "Add Expense":
            categories = finance_manager.get_categories()
            if categories == []:
                sg.popup_error("No categories available. Please add a category first.")
                continue
            data = add_transaction_window(categories, "expense")
            if data:
                try:
                    amount = float(data["amount"])
                except ValueError:
                    sg.popup_error("Amount must be a number.")
                    continue
                finance_manager.add_transaction(data["title"], amount, data["category"], data["type"])            
                save_transactions(finance_manager.get_transactions())
                sg.popup("Expense added!")

        if event == "Add Income":
            categories = finance_manager.get_categories()
            if categories == []:
                sg.popup_error("No categories available. Please add a category first.")
                continue
            data = add_transaction_window(categories, "income")
            if data:
                try:
                    amount = float(data["amount"])
                except ValueError:
                    sg.popup_error("Amount must be a number.")
                    continue
                finance_manager.add_transaction(data["title"], amount, data["category"], data["type"])
                save_transactions(finance_manager.get_transactions())
                sg.popup("Income added!")

        window["TABLE"].update(
            [[t.title, t.amount, t.category.name, t.type] for t in finance_manager.get_transactions()]
        )

    window.close()

