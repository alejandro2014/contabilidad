from src.services.BaseService import BaseService

class ExpenseTypesService(BaseService):
    def __init__(self):
        super().__init__()

    def select_expense_types_full(self):
        sql = self.sql_generator.select_expense_types_full()

        expense_types_full = self.db.select(sql)

        return map(lambda expense_type_full: {
            'category': expense_type_full[0],
            'comment': expense_type_full[1]
        }, expense_types_full)

    def get_expense_types_count(self):
        sql = self.sql_generator.select_expense_types_count()

        return self.db.select(sql)[0][0]

    def get_category_names(self):
        sql = self.sql_generator.select_expense_types_names()

        category_names = self.db.select(sql)

        return map(lambda category_name: category_name[0], category_names)

    def remove_category(self, category):
        sql = self.sql_generator.delete_expense_type({ 'category': category })

        self.db.delete(sql)

    def check_category_exists(self, category_name):
        sql = self.sql_generator.select_category_name(category_name)

        categories_existent = self.db.select(sql)[0][0]

        return categories_existent > 0

    def add_category(self, category_name, category_description, is_savings, is_income):
        category = {
            'name': category_name,
            'description': category_description,
            'is_savings': is_savings,
            'is_income': is_income
        }

        sql = self.sql_generator.insert_category(category)

        self.db.insert(sql)
