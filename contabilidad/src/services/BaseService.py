from src.zz_old_dao.SqliteConnector import SqliteConnector
from src.zz_old_dao.SqlGenerator import SqlGenerator

class BaseService:
    def __init__(self):
        self.print_sql_flag = False
        self.db = SqliteConnector(self.print_sql_flag)
        self.excl_categories = self.get_excluded_categories()
        self.sql_generator = SqlGenerator(self.excl_categories)

    def get_excluded_categories(self):
        sql = "select category from expense_types where is_income is 'True'"
        incomes_categories = self.db.select(sql)
        incomes_categories = [ ic[0] for ic in incomes_categories ]

        sql = "select category from expense_types where is_savings is 'True'"
        savings_categories = self.db.select(sql)
        savings_categories = [ sc[0] for sc in savings_categories ]

        return {
            'incomes': incomes_categories,
            'savings': savings_categories
        }

    def get_single_value(self, sql):
        count = self.db.select(sql)

        return count[0][0]

    def insert(self, sql):
        inserted = True
        value = "OK"

        try:
            self.db.insert(sql)
        except:
            value = "ERROR"
            inserted = False

        self.print_sql("[" + value + "] " + sql)

        return inserted

    def delete(self, sql):
        deleted = True
        value = "OK"

        try:
            self.db.delete(sql)
        except:
            value = "ERROR"
            deleted = False

        self.print_sql("[" + value + "] " + sql)

        return deleted

    def print_sql(self, sql):
        if self.print_sql_flag:
            print(sql)
