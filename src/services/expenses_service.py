from src.dao.expenses_dao import ExpensesDao

class ExpensesService:
    def __init__(self, dao=None):
        self.dao = ExpensesDao() if dao is None else dao

    def load_expenses(self, expenses):
        return self.dao.load_expenses(expenses)
    
    def get_pending_expenses(self):
        return self.dao.get_pending_expenses()