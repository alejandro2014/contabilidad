from src.services.BaseService import BaseService
from src.services.formatters.PendingExpensesFormatter import PendingExpensesFormatter

class PendingExpensesService(BaseService):
    def __init__(self):
        super().__init__()
        self.formatter = PendingExpensesFormatter()

    def add_expense(self, line, formatter):
        expense = self.formatter.csv_to_expense(line, formatter)
        sql = self.sql_generator.insert_pending_expense(expense)

        return self.insert(sql)

    def get_expenses(self, filter = None):
        sql = self.sql_generator.select_pending_expenses(filter)
        expenses = self.db.select(sql)

        return self.formatter.format_expenses(expenses)

    def classify_expenses(self, expenses, category):
        for expense in expenses:
            add_expense_sql = self.sql_generator.insert_classified_expense(expense, category)
            delete_old_expense_sql = self.sql_generator.delete_pending_expense(expense)

            self.insert(add_expense_sql)
            self.delete(delete_old_expense_sql)

    def get_expenses_count(self):
        sql = self.sql_generator.select_pending_expenses_count()

        return self.get_single_value(sql)
