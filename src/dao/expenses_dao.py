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
        # The whole file in a single transaction: when something fails nothing is loaded
        self.db.backup()

        rows = [ self.sql_generator.expense_values(e) for e in expenses ]
        successes_number = self.db.execute_many(self.sql_generator.insert_expenses(), rows)

        # The ones not inserted were already in the database
        return successes_number, len(expenses) - successes_number
    
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

    def update_unclassified_expense(self, expense_id):
        sql = self.sql_generator.update_unclassified_expense(expense_id)

        self.db.execute_sql(sql)

    def get_pending_expenses_count(self):
        sql = self.sql_generator.select_pending_expenses_count()

        return self.db.select(sql)[0][0]

    def get_classified_expenses_count(self):
        sql = self.sql_generator.select_classified_expenses_count()

        return self.db.select(sql)[0][0]

    def get_expenses_date_range(self):
        sql = self.sql_generator.select_expenses_date_range()

        # Classified and pending expenses, None when there are no expenses of that kind
        date_range = { 'classified': None, 'pending': None }

        for e in self.db.select(sql):
            date_range['classified' if e[0] else 'pending'] = {
                'min_date': e[1],
                'max_date': e[2],
                'count': e[3]
            }

        return date_range