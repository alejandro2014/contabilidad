from model import Expense

class ExpensesDao:
    def __init__(self, db_connector):
        self._db = db_connector

    def add_expense(self, expense):
        sql = "INSERT INTO expenses (date_record, concept, amount, category1, category2, tag1, tag2, hash) VALUES (?,?,?,?,?,?,?)"
        params = (expense.date,
                expense.concept,
                expense.amount,
                expense.category1,
                expense.category2,
                expense.tag1,
                expense.tag2,
                expense.hash)

        self._db.run_sql(sql, params)

    def add_expenses(self, expenses):
        for expense in expenses:
            self.add_expense(expense)

    def delete_expense(self, expense):
        sql = "DELETE FROM expenses WHERE date_record = ? AND concept = ? AND amount = ?"
        params = (expense.date, expense.concept, expense.amount)

        self._db.run_sql(sql, params)

    def delete_expenses(self, file_hash):
        sql = "DELETE FROM expenses WHERE hash = ?"
        params = (file_hash,)

        self._db.run_sql(sql, params)

    def update_category(self, expense_id, category):
        sql = f"UPDATE expenses SET category1 = '{category}' WHERE id = '{expense_id}'"

        self._db.update(sql)

    def unclassify_by_id(self, expense_id):
        sql = f"UPDATE expenses SET category1 = NULL WHERE id = '{expense_id}'"

        self._db.update(sql)

    def unclassify_by_file_hash(self, file_hash, search=None, condition=None):
        sql = f"UPDATE expenses SET category1 = NULL WHERE hash = '{file_hash}'"

        self.update_hola(sql, search, condition)

    def unclassify_by_date_and_search(self, date, search=None, condition=None):
        sql = f"UPDATE expenses SET category1 = NULL WHERE date_record = '{date}'"

        self.update_hola(sql, search, condition)

    def unclassify_by_dates_fromto_and_search(self, date_from, date_to, search=None, condition=None):
        sql = f"UPDATE expenses SET category1 = NULL WHERE"

        if date_from is not None and date_to is not None:
            sql = f"{sql} date_record >= '{date_from}' AND date_record <= '{date_to}'"
        elif date_from is not None and date_to is None:
            sql = f"{sql} date_record >= '{date_from}'"
        elif date_from is None and date_to is not None:
            sql = f"{sql} date_record <= '{date_to}'"

        self.update_hola(sql, search, condition)

    def unclassify_by_search_and_condition(self, search=None, condition=None):
        sql = f"UPDATE expenses SET category1 = NULL WHERE 1 = 1"

        self.update_hola(sql, search, condition)

    def update_hola(self, sql, search=None, condition=None):
        if search is not None:
            sql = f"{sql} and concept like '%{search}%'"

        if condition is not None:
            sql = f"{sql} and {condition}"

        self._db.update(sql)

    def get_expenses(self, expense_type=None, ids=None, file_hash=None,
                     search=None, date=None, date_from=None, date_to=None,
                     condition=None):
        sql = f"SELECT * FROM expenses WHERE 1 = 1"

        if ids is not None:
            sql = f'{sql}{self.get_sql_ids(ids)}'
        elif file_hash is not None:
            sql = f"{sql} AND hash = '{file_hash}'"

        if date is not None:
            sql = f"{sql} AND date_record = '{date}'"
        elif date_from is not None or date_to is not None:
            sql = f'{sql}{self.get_sql_dates_fromto(date_from, date_to)}'

        sql = f'{sql}{self.get_sql_rest(expense_type, search, condition)}'
        return self.get_expenses_by_sql(sql)

    def get_sql_ids(self, ids):
        ids_list = ids.split(',')
        ids = ', '.join([f"'{id}'" for id in ids_list])

        return f" AND id IN ({ids})"

    def get_sql_dates_fromto(self, date_from=None, date_to=None):
        if date_from is not None and date_to is not None:
            sql = f" AND date_record >= '{date_from}' AND date_record <= '{date_to}'"
        elif date_from is not None and date_to is None:
            sql = f" AND date_record >= '{date_from}'"
        elif date_from is None and date_to is not None:
            sql = f" AND date_record <= '{date_to}'"

        return sql

    def get_sql_rest(self, expense_type=None, search=None, condition=None):
        sql = ''

        if expense_type is not None:
            null_status = "NOT NULL" if expense_type == 'classified' else "NULL"
            sql = f"{sql} AND category1 IS {null_status}"

        if search is not None:
            sql = f"{sql} AND concept like '%{search}%'"

        if condition is not None:
            sql = f"{sql} AND {condition}"

        return sql

    def get_expenses_by_sql(self, sql):
        raw_result = self._db.select(sql)

        return [
            Expense(
                id=r[0]
            ) for r in raw_result
        ]
        return [{
            'id': r[0],
            'file': r[1],
            'date': r[2],
            'category1': r[5],
            'concept': r[3],
            'amount': r[4]
        } for r in raw_result]