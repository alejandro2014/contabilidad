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

        return successes_number, errors_number
    
    def get_pending_expenses(self, filter=None, sort_by=None):
        #sql = self.sql_generator.select_pending_expenses(filter, sort_by)
        sql = self.sql_generator.select_pending_expenses(filter, 'amount')
        expenses_db = self.db.select(sql)

        return [
            Expense(
                id = e[0],
                date = e[1],
                title = e[2],
                amount = e[3]
            ) for e in expenses_db
        ]
    
    def get_classified_expenses(self, filter=None, sort_by=None):
        sql = self.sql_generator.select_classified_expenses(filter, sort_by)
        expenses_db = self.db.select(sql)

        return [
            Expense(
                id = e[0],
                date = e[1],
                title = e[2],
                amount = e[3],
                category = e[4]
            ) for e in expenses_db
        ]

    def get_classified_expenses_by_month(self):
        sql = self.sql_generator.select_classified_expenses_by_month()

        return [ {
            'month': e[0],
            'quantity': str(round(e[1], 2))
        } for e in self.db.select(sql) ]

    def get_classified_expenses_by_type(self):
        sql = self.sql_generator.select_classified_expenses_by_type()

        return [ {
            'type': e[0],
            'quantity': str(round(e[1], 2))
        } for e in self.db.select(sql) ]

    def get_classified_expenses_by_type_and_month(self):
        sql = self.sql_generator.select_classified_expenses_by_type_and_month()

        return [ {
            'type': e[0],
            'month': e[1],
            'quantity': str(round(e[2], 2))
        } for e in self.db.select(sql) ]

    def update_classified_expense(self, expense_id, category):
        sql = self.sql_generator.update_classified_expense(expense_id, category)
        
        self.db.execute_sql(sql)

    def get_pending_expenses_count(self):
        sql = self.sql_generator.select_pending_expenses_count()

        return self.db.select(sql)[0][0]

    def get_classified_expenses_count(self):
        sql = self.sql_generator.select_classified_expenses_count()

        return self.db.select(sql)[0][0]