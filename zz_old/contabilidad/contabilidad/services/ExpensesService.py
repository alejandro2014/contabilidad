from services.BaseService import BaseService

class ExpensesService(BaseService):
    def __init__(self):
        super().__init__()

    def add_expense(self, line):
        concept_line = {
            'date': line['field_0'],
            'concept': line['field_3'],
            'value': line['field_5'].replace(',', '')
        }

        inserted = True
        sql = self.sql_generator.insert_expense_not_classified(concept_line)
        value = "OK"

        try:
            self.db.insert(sql)
        except:
            value = "ERROR"
            inserted = False

        print("[" + value + "] " + sql)

        return inserted

    def get_all_expenses(self):
        sql = self.sql_generator.get_all_expenses()

        expenses = self.db.select(sql)

        return map(lambda expense: {
            'date': expense[0],
            'concept': expense[1],
            'quantity': str(expense[2]),
            'type': expense[3]
        }, expenses)
