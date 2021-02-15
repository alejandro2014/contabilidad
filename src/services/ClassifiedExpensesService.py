from src.services.BaseService import BaseService
from src.services.formatters.ClassifiedExpensesFormatter import ClassifiedExpensesFormatter

class ClassifiedExpensesService(BaseService):
    def __init__(self):
        super().__init__()
        self.formatter = ClassifiedExpensesFormatter()

    def add_expense(self, line):
        expense = self.formatter.csv_to_expense(line)
        sql = self.sql_generator.insert_expense_not_classified(expense)

        return self.insert(sql)

    def get_expenses(self, filter = None):
        sql = self.sql_generator.select_classified_expenses(filter)
        expenses = self.db.select(sql)

        return self.formatter.format_expenses(expenses)

    def get_expenses_by_month(self):
        sql = self.sql_generator.select_classified_expenses_by_month()
        expenses = self.db.select(sql)

        return self.formatter.format_expenses_by_month(expenses)

    def get_expenses_by_type(self):
        sql = self.sql_generator.select_classified_expenses_by_type()
        expenses = self.db.select(sql)

        return self.formatter.format_expenses_by_type(expenses)

    def get_expenses_by_type_and_month(self):
        sql = self.sql_generator.select_classified_expenses_by_type_and_month()
        expenses = self.db.select(sql)

        return self.formatter.format_expenses_by_type_and_month(expenses)

    def get_expenses_count(self):
        sql = self.sql_generator.select_classified_expenses_count()

        return self.get_single_value(sql)
