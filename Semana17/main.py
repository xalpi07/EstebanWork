from interfaces import main_window
from logic import FinanceManager
    
if __name__ == "__main__":
    finance_manager = FinanceManager()
    main_window(finance_manager)