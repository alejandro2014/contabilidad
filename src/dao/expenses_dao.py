from sqlite3 import IntegrityError

from src.dao.SqlGenerator import SqlGenerator
from src.dao.SqliteConnector import SqliteConnector

class ExpensesDao:
    def __init__(self):
        self.sql_generator = SqlGenerator()
        self.db = SqliteConnector()

    def load_expenses(self, expenses):
        successes_number = 0
        errors_number = 0

        for expense in expenses:
            sql = self.sql_generator.insert_expense(expense)

            try:
                self.db.insert(sql)
                successes_number += 1
            except IntegrityError:
                errors_number += 1

        return (successes_number, errors_number)
    
    def get_pending_expenses(self):
        sql = self.sql_generator.select_pending_expenses()
        expenses = self.db.select(sql)

        return expenses
            

