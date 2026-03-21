from services.BaseService import BaseService

class ExpenseTypesService(BaseService):
    def __init__(self):
        super().__init__()

    def get_expense_types_full(self):
        sql = self.sql_generator.get_expense_types_full()

        expense_types_full = self.db.select(sql)

        return map(lambda expense_type_full: {
            'category': expense_type_full[0],
            'comment': expense_type_full[1]
        }, expense_types_full)
