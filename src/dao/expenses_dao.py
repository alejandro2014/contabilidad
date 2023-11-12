from sqlite3 import IntegrityError

from src.model.expense import Expense
from src.dao.SqlGenerator import SqlGenerator
from src.dao.SqliteConnector import SqliteConnector

class ExpensesDao:
    def __init__(self, 
                 sql_generator=SqlGenerator(), 
                 db=SqliteConnector()):
        self.sql_generator = sql_generator
        self.db = db

    def load_expenses(self, expenses):
        successes_number = 0
        errors_number = 0

        for expense in expenses:
            sql = self.sql_generator.insert_expense(expense)

            try:
                self.db.execute_sql(sql)
                successes_number += 1
            except IntegrityError:
                errors_number += 1

        return (successes_number, errors_number)
    
    def get_pending_expenses(self, filter=None, sort_by=None):
        sql = self.sql_generator.select_pending_expenses(filter, sort_by)
        expenses_db = self.db.select(sql)

        return [
            Expense(
                id = e[0],
                date = e[1],
                title = e[2],
                amount = e[3]
            ) for e in expenses_db
        ]
    
    def update_classified_expense(self, expense_id, category):
        sql = self.sql_generator.update_classified_expense(expense_id, category)
        self.db.execute_sql(sql)
            

