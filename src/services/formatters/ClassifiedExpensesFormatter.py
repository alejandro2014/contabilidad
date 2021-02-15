from DateConverter import DateConverter

class ClassifiedExpensesFormatter:
    def csv_to_expense(self, csv_line):
        return {
            'date': DateConverter().format_raw(csv_line['field_0']),
            'concept': csv_line['field_3'],
            'value': csv_line['field_5'].replace(',', '')
        }

    def format_expenses(self, expenses):
        return list(map(lambda expense: {
            'date': expense[0],
            'concept': expense[1],
            'type': expense[2],
            'quantity': str(expense[3])
        }, expenses))

    def format_expenses_by_month(self, expenses):
        return list(map(lambda expense: {
            'month': expense[0],
            'quantity': str(round(expense[1], 2))
        }, expenses))

    def format_expenses_by_type(self, expenses):
        return list(map(lambda expense: {
            'type': expense[0],
            'quantity': str(round(expense[1], 2))
        }, expenses))

    def format_expenses_by_type_and_month(self, expenses):
        return list(map(lambda expense: {
            'type': expense[0],
            'month': expense[1],
            'quantity': str(round(expense[2], 2))
        }, expenses))
