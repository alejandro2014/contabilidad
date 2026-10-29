from src.model.expense import Expense
from src.dao.SqlGenerator import SqlGenerator
from src.dao.SqliteConnector import SqliteConnector

class ExpensesDao:
    def __init__(self, 
                 sql_generator=SqlGenerator(), 
                 db=SqliteConnector.shared()):
        self.sql_generator = sql_generator
        self.db = db

    def load_expenses(self, expenses):
        # The whole file in a single transaction: when something fails nothing is loaded
        self.db.backup()

        rows = [ self.sql_generator.expense_values(e) for e in expenses ]

        # The movements already loaded are updated with their balance, so the rows changed are not the ones inserted
        count_before = self.get_expenses_count()
        self.db.execute_many(self.sql_generator.insert_expenses(), rows)
        successes_number = self.get_expenses_count() - count_before

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
                category = e[4],
                note = e[5],
                tags = self.split_tags(e[6])
            ) for e in expenses_db
        ]

    def split_tags(self, tags):
        return [] if tags is None else sorted(tags.split(self.sql_generator.TAGS_SEPARATOR), key=str.casefold)

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

    def update_notes_and_tags(self, expense_ids, note, tags):
        # The note and the tags of every expense are replaced, all of them together
        queries = []

        for expense_id in expense_ids:
            queries.append(self.sql_generator.update_expense_note(expense_id, note))
            queries.append(self.sql_generator.delete_expense_tags(expense_id))
            queries += [ self.sql_generator.insert_expense_tag(expense_id, tag) for tag in tags ]

        self.db.execute_transaction(queries)

    def get_tags(self):
        return [ t[0] for t in self.db.select(self.sql_generator.select_tags()) ]

    def get_tag_totals(self, filter=None):
        # Expenses are negative amounts, like in the other grouped tables
        return [ {
            'tag': t[0],
            'quantity': str(round(t[1], 2)),
            'count': str(t[2])
        } for t in self.db.select(self.sql_generator.select_tag_totals(filter)) ]

    def get_expenses_count(self):
        return self.db.select(self.sql_generator.select_expenses_count())[0][0]

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