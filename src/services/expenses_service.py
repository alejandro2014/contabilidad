from src.dao.expenses_dao import ExpensesDao

class ExpensesService:
    def __init__(self, dao=None):
        self.dao = ExpensesDao() if dao is None else dao

    def load_expenses(self, expenses):
        return self.dao.load_expenses(expenses)
    
    def get_pending_expenses(self, filter=None, sort_by=None):
        return self.dao.get_pending_expenses(filter, sort_by)
    
    def classify_expenses(self, expense_ids, category):
        for expense_id in expense_ids:
            self.dao.update_classified_expense(expense_id, category)

    def get_classified_expenses_by_month(self):
        return self.dao.get_classified_expenses_by_month()

    def get_classified_expenses_by_type(self):
        return self.dao.get_classified_expenses_by_type()

    def get_classified_expenses_by_type_and_month(self):
        return self.dao.get_classified_expenses_by_type_and_month()