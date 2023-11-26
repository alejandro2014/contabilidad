from src.services.BaseService import BaseService

class ExpenseTypesService(BaseService):
    def __init__(self):
        super().__init__()

    def get_categories_simple(self):
        sql = self.sql_generator.select_expense_types_simple()

        categories_simple = self.db.select(sql)

        return [ c[0] for c in categories_simple ]

    def select_expense_types_full(self):
        sql = self.sql_generator.select_expense_types_full()

        expense_types_full = self.db.select(sql)

        return [ {
            'category': etf[0],
            'comment': etf[1]
        } for etf in expense_types_full ]

    def remove_category(self, category):
        sql = self.sql_generator.delete_expense_type(category)

        self.db.execute_sql(sql)

    def check_category_exists(self, category_name):
        sql = self.sql_generator.select_category_name(category_name)

        categories_existent = self.db.select(sql)[0][0]

        return categories_existent > 0

    def add_category(self, category_name, category_description):
        sql = self.sql_generator.insert_category(category_name, category_description)

        self.db.execute_sql(sql)

    def update_expense_type(self, old_category, old_comment, field, new_value):
        sql = self.sql_generator.update_expense_type(old_category, old_comment, field, new_value)

        self.db.execute_sql(sql)
