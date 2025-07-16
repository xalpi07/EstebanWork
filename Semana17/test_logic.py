import pytest
from logic import FinanceManager

def test_add_category():
    fm = FinanceManager()
    fm.add_category("Food")
    assert len(fm.get_categories()) == 1
    assert fm.get_categories()[0].name == "Food"

def test_add_multiple_categories():
    fm = FinanceManager()
    fm.add_category("Food")
    fm.add_category("Transport")
    fm.add_category("Salary")
    names = [c.name for c in fm.get_categories()]
    assert names == ["Food", "Transport", "Salary"]

def test_add_transaction_success():
    fm = FinanceManager()
    fm.add_category("Salary")
    fm.add_transaction("Monthly Salary", 5000, "Salary", "income")
    transactions = fm.get_transactions()
    assert len(transactions) == 1
    assert transactions[0].title == "Monthly Salary"
    assert transactions[0].amount == 5000
    assert transactions[0].category.name == "Salary"
    assert transactions[0].type == "income"

def test_add_expense_transaction():
    fm = FinanceManager()
    fm.add_category("Food")
    fm.add_transaction("Lunch", 100, "Food", "expense")
    t = fm.get_transactions()[0]
    assert t.title == "Lunch"
    assert t.amount == 100
    assert t.type == "expense"

def test_add_transaction_category_not_found():
    fm = FinanceManager()
    with pytest.raises(ValueError, match="Category not found"):
        fm.add_transaction("Lunch", 100, "Food", "expense")

def test_get_categories_empty():
    fm = FinanceManager()
    assert fm.get_categories() == []

def test_get_transactions_empty():
    fm = FinanceManager()
    assert fm.get_transactions() == []

def test_add_transaction_with_float_amount():
    fm = FinanceManager()
    fm.add_category("Entertainment")
    fm.add_transaction("Movie", 12.5, "Entertainment", "expense")
    t = fm.get_transactions()[0]
    assert isinstance(t.amount, float)
    assert t.amount == 12.5